from src import fec
import shutil
import zipfile
import urllib.request


def test_fetch_candidate_totals_pagination(monkeypatch):
    def fake_get_json(url, params):
        page = params.get("page", 1)
        if page == 1:
            return {
                "results": [{"page": 1}],
                "pagination": {"page": 1, "pages": 2},
            }
        return {
            "results": [{"page": 2}],
            "pagination": {"page": 2, "pages": 2},
        }

    monkeypatch.setattr(fec, "get_json", fake_get_json)
    data = fec.fetch_candidate_totals("H0XX00001", 2024)
    assert [d["page"] for d in data] == [1, 2]


def test_fetch_independent_expenditures_pagination(monkeypatch):
    def fake_get_json(url, params):
        page = params.get("page", 1)
        if page == 1:
            return {
                "results": [{"i": 1}],
                "pagination": {"page": 1, "pages": 3},
            }
        if page == 2:
            return {
                "results": [{"i": 2}],
                "pagination": {"page": 2, "pages": 3},
            }
        return {
            "results": [{"i": 3}],
            "pagination": {"page": 3, "pages": 3},
        }

    monkeypatch.setattr(fec, "get_json", fake_get_json)
    data = fec.fetch_independent_expenditures("H0XX00001", 2024)
    assert len(data) == 3


def test_fetch_candidate_totals_bulk(monkeypatch, tmp_path):
    data = "CAND_ID,TTL_RECEIPTS\nH0XX00001,100\nH0XX00002,50\n"
    zip_file = tmp_path / "ccl.csv.zip"
    with zipfile.ZipFile(zip_file, "w") as z:
        z.writestr("ccl.csv", data)

    def fake_urlretrieve(url, dest):
        shutil.copy(zip_file, dest)
        return str(dest), None

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_urlretrieve)
    rows = fec.fetch_candidate_totals("H0XX00001", 2024, bulk=True)
    assert rows == [{"CAND_ID": "H0XX00001", "TTL_RECEIPTS": "100"}]
