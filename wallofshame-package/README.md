
# Wall of Shame + Financial Alignments (Static Package)

A ready-to-deploy static site bundle. Upload this folder to your GitHub repo and enable GitHub Pages.  
**Demo data only** is included (fictional names + donors). Replace files under `accountability/data/` with real exports.

## Structure
```
accountability/
  index.html                # Wall of Shame
  financial-alignments.html # Financial Alignments page
  assets/
    css/styles.css
    js/utils.js
  images/
    no-photo.png
    S000001.png ...         # placeholder avatars
  data/
    members.json            # array[{ bioguide, name, state, district, party, photo? }]
    votes.json              # { BILLKEY: { title, date, href, meaning, offenders:[{bioguide, vote}] } }
    donors-by-member.json   # { bioguide: [ {name, total, count, industry, fec_id} ] }
    vote-alignments.json    # { bioguide: percent }
    badges.json             # { BILLKEY: { badge, color, description } }
    member-awards.json      # optional/placeholder
```

## Deploy (GitHub Pages)
1. Create a repo and copy this folder's contents.
2. Commit + push:
   ```bash
   git add -A
   git commit -m "add wall of shame demo site"
   git push origin main
   ```
3. In **Settings → Pages**, set *Source* to **Deploy from a branch**, choose `main` and `/ (root)`.
4. Open `https://<your-domain-or-user>.github.io/<repo>/accountability/`

## Updating with real data
- Replace `accountability/data/*.json` with your generated files.
- `members.json` photo paths can point to URLs or `accountability/images/<file>.png`.
- `votes.json` lists "offenders" for each bill by `bioguide` (the page highlights them first).
- `donors-by-member.json` top donor shows on each card; "View receipts" lists all donors.

The JS loader tries multiple paths (`data/...`, `../data/...`, `/data/...`) so it works both locally and on Pages.
