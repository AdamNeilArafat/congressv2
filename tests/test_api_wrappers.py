from src import bills


def test_fetch_bills_pagination_and_headers(monkeypatch):
    calls = []

    def fake_get_json(url, params=None, headers=None):
        calls.append({"url": url, "params": params, "headers": headers})
        if len(calls) == 1:
            return {
                "bills": {"bill": [{"billId": "b1"}]},
                "pagination": {"next": "next-url"},
            }
        return {"bills": {"bill": [{"billId": "b2"}]}}

    class Dummy:
        congress_api_key = "KEY"

    monkeypatch.setattr(bills, "get_json", fake_get_json)
    monkeypatch.setattr(bills, "get_settings", lambda: Dummy())
    items = bills.fetch_bills(from_date="2020-01-01")
    assert items == [{"billId": "b1"}, {"billId": "b2"}]
    assert calls[0]["params"]["fromDateTime"] == "2020-01-01"
    assert calls[0]["headers"]["X-Api-Key"] == "KEY"
    assert calls[1]["params"] is None
