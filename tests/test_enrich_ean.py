from src.enrichment.ean import enhance_ean

def test_ean_extraction():
    rec = {"title": "Product", "barcode": "1234567890123"}
    out = enhance_ean(rec.copy())
    assert out["ean"] == "1234567890123"

def test_ean_preserved():
    rec = {"ean": "7891234567895"}
    out = enhance_ean(rec.copy())
    assert out["ean"] == "7891234567895"
