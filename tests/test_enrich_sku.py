from src.enrichment.sku import enhance_sku

def test_sku_generated():
    rec = {"title": "Sony Headphones", "brand": "Sony"}
    out = enhance_sku(rec.copy())
    assert "sku" in out
    assert out["sku"].startswith("SON")
    assert len(out["sku"]) > 5

def test_sku_preserved():
    rec = {"title": "Sony Headphones", "sku": "SONY-1234"}
    out = enhance_sku(rec.copy())
    assert out["sku"] == "SONY-1234"
