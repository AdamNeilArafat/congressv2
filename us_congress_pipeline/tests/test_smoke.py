import subprocess
import sys
from pathlib import Path
import zipfile
import csv

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pipeline import paths


def run(cmd: list[str]) -> None:
    env = {"PYTHONPATH": str(SRC)}
    subprocess.run([sys.executable, "-m", "pip", "install", "pyyaml", "tqdm", "lxml"], check=True)
    subprocess.run(cmd, check=True, cwd=ROOT, env=env)


def create_fixtures() -> None:
    raw_leg = paths.RAW_DIR / "congress-legislators"
    raw_leg.mkdir(parents=True, exist_ok=True)
    yaml_content = """
- id:
    bioguide: A000001
    fec:
      - H0XX00001
  name:
    first: Alice
    last: Smith
  terms:
    - type: rep
      start: 2023-01-03
      end: 2025-01-03
      party: Democrat
      state: XX
      district: 1
"""
    (raw_leg / "legislators-current.yaml").write_text(yaml_content)

    roll_dir = paths.RAW_DIR / "rollcalls" / "118"
    roll_dir.mkdir(parents=True, exist_ok=True)
    xml = """
<rollcall>
 <vote_id>1</vote_id>
 <chamber>house</chamber>
 <congress>118</congress>
 <session>1</session>
 <rollnumber>1</rollnumber>
 <date>2023-01-01</date>
 <question>On Passage</question>
 <result>Passed</result>
 <records>
  <record>
   <id>A000001</id>
   <vote>Yea</vote>
  </record>
 </records>
</rollcall>
"""
    (roll_dir / "vote1.xml").write_text(xml)

    fec_dir = paths.RAW_DIR / "fec" / "2024"
    fec_dir.mkdir(parents=True, exist_ok=True)
    import pandas as pd
    def zwrite(name, header, rows):
        df = pd.DataFrame(rows, columns=header)
        csv_data = df.to_csv(index=False)
        with zipfile.ZipFile(fec_dir / f"{name}.zip", "w") as zf:
            zf.writestr(f"{name}.csv", csv_data)
    zwrite("candidates", ["CAND_ID","NAME","PARTY","STATE","DISTRICT"], [["H0XX00001","Alice for Congress","DEM","XX","01"]])
    zwrite("candidate_totals", ["CAND_ID","TOTAL_RECEIPTS"], [["H0XX00001","1000"]])
    zwrite("indiv_contrib", ["CAND_ID","TRANSACTION_AMT"], [["H0XX00001","50"],["H0XX00001","300"]])


def test_pipeline_smoke(tmp_path):
    run([sys.executable, "-m", "pipeline.cli", "init"])
    create_fixtures()
    run([sys.executable, "-m", "pipeline.cli", "extract"])
    run([sys.executable, "-m", "pipeline.cli", "link"])
    run([sys.executable, "-m", "pipeline.cli", "metrics", "--cycles", "2024", "--congresses", "118"])
    out = paths.OUTPUT_DIR / "candidate_finance_summary_2024.csv"
    assert out.exists()
    df = pd.read_csv(out)
    assert "cand_id" in df.columns
    vote_out = paths.OUTPUT_DIR / "incumbent_vote_summary_118.csv"
    assert vote_out.exists()
