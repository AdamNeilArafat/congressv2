# scripts/fec_analyze.py
import os, re, csv, sys, math, json
from pathlib import Path
import pandas as pd

# ---------- CONFIG ----------
FEC_ROOT   = Path("FEC")
OUT_DIR    = Path("analysis_output")
CHUNKSIZE  = 250_000          # adjust if you hit memory limits
MIN_AMT    = -10_000_000.0    # sanity range filter
MAX_AMT    =  10_000_000.0
# ----------------------------

OUT_DIR.mkdir(parents=True, exist_ok=True)

def sniff_delimiter(sample: str):
    if "|" in sample: return "|"
    if "\t" in sample: return "\t"
    if "," in sample: return ","
    if "\x1c" in sample: return "\x1c"  # ASCII 28
    return "|"

def looks_state(s):
    return isinstance(s, str) and len(s)==2 and s.isalpha() and s.isupper()

def pick_amount_col(df):
    # Try by name first
    for pat in [r'amount', r'amt', r'transaction[_ ]?amt', r'expenditure[_ ]?amt', r'disb.*amt', r'total']:
        for c in df.columns:
            if re.search(pat, str(c), re.I):
                return c
    # Fallback: choose a numeric-like column with money-looking values
    candidates = []
    head = df.head(500)
    for c in df.columns:
        s = head[c].astype(str).str.replace(r'[,\$\s]', '', regex=True)
        ok = pd.to_numeric(s, errors='coerce')
        # accept if >30% of sample are numbers and at least one abs(value) > 0
        if (ok.notna().mean() > 0.3) and (ok.abs().max() > 0):
            candidates.append((c, ok.notna().mean(), ok.abs().median()))
    if candidates:
        # prefer higher numeric ratio and larger median magnitude
        candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
        return candidates[0][0]
    return None

def pick_state_col(df):
    # Named columns
    for pat in [r'state', r'\bst\b']:
        for c in df.columns:
            if re.search(pat, str(c), re.I):
                return c
    # Heuristic over sample rows
    head = df.head(1000)
    best, score = None, -1
    for c in df.columns:
        sc = head[c].apply(looks_state).mean()
        if sc > score:
            score, best = sc, c
    return best

def pick_name_col(df):
    for pat in [r'(payee|recipient|name|committee)', r'candidate']:
        for c in df.columns:
            if re.search(pat, str(c), re.I):
                return c
    return None

def coerce_amount(s):
    s = s.astype(str).str.replace(r'[,\$]', '', regex=True)
    v = pd.to_numeric(s, errors='coerce')
    v = v.where(v.between(MIN_AMT, MAX_AMT))
    return v

def read_chunked(path: Path, sep: str):
    try:
        # try with header auto
        return pd.read_csv(path, sep=sep, dtype=str, chunksize=CHUNKSIZE,
                           quoting=csv.QUOTE_NONE, on_bad_lines='skip', low_memory=True)
    except Exception:
        # headerless
        return pd.read_csv(path, sep=sep, dtype=str, header=None, chunksize=CHUNKSIZE,
                           quoting=csv.QUOTE_NONE, on_bad_lines='skip', low_memory=True)

def process_file(path: Path):
    # sniff delim from head
    with open(path, 'rb') as f:
        sample = f.read(65536).decode('utf-8', 'ignore')
    sep = sniff_delimiter(sample)
    chunks = list(read_chunked(path, sep))

    # Prime with first chunk to pick columns
    first = next(iter(chunks))
    first = first.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    amt_col  = pick_amount_col(first)
    st_col   = pick_state_col(first)
    name_col = pick_name_col(first)

    # If headerless, name columns numerically to keep consistency
    if not hasattr(first, "columns"):
        first.columns = list(range(len(first.columns)))

    # rollups
    rows = 0
    by_state = {}
    by_name  = {}

    def add_rollups(df):
        nonlocal rows
        rows += len(df)
        if amt_col not in df.columns:
            return
        amt = coerce_amount(df[amt_col])
        if st_col in df.columns:
            g = df.assign(_amt=amt).groupby(st_col, dropna=False)['_amt'].sum()
            for k, v in g.items():
                by_state[k] = by_state.get(k, 0.0) + (0.0 if pd.isna(v) else float(v))
        if name_col in df.columns:
            g = df.assign(_amt=amt).groupby(name_col, dropna=False)['_amt'].sum().nlargest(1000)
            for k, v in g.items():
                by_name[k] = by_name.get(k, 0.0) + (0.0 if pd.isna(v) else float(v))

    add_rollups(first)
    # process remaining chunks
    for ch in read_chunked(path, sep):
        ch = ch.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        add_rollups(ch)

    meta = {
        "file": str(path),
        "rows": rows,
        "amount_col": str(amt_col),
        "state_col": str(st_col),
        "name_col": str(name_col),
        "delimiter": sep
    }

    return meta, by_state, by_name

def main():
    files = sorted([p for p in FEC_ROOT.rglob("*.txt") if p.is_file()])
    inventory = []
    grand_state = {}
    grand_name  = {}
    for p in files:
        try:
            meta, st, nm = process_file(p)
            inventory.append(meta)
            for k, v in st.items():
                grand_state[k] = grand_state.get(k, 0.0) + v
            for k, v in nm.items():
                grand_name[k] = grand_name.get(k, 0.0) + v
            print(f"OK  {p}  rows={meta['rows']}  amt={meta['amount_col']}  state={meta['state_col']}  name={meta['name_col']}")
        except Exception as e:
            print(f"ERR {p}: {e}")

    inv_df = pd.DataFrame(inventory).sort_values("file")
    inv_df.to_csv(OUT_DIR / "file_inventory.csv", index=False)

    st_df = (pd.Series(grand_state, name="total_amount")
               .sort_values(ascending=False)
               .rename_axis("state").reset_index())
    st_df.to_csv(OUT_DIR / "rollup_by_state.csv", index=False)

    nm_df = (pd.Series(grand_name, name="total_amount")
               .sort_values(ascending=False)
               .rename_axis("name_or_committee").reset_index())
    nm_df.to_csv(OUT_DIR / "rollup_by_name_or_committee.csv", index=False)

    print("\nWrote:")
    for f in ["file_inventory.csv","rollup_by_state.csv","rollup_by_name_or_committee.csv"]:
        print(OUT_DIR / f)

if __name__ == "__main__":
    main()
