from src.enrichment.color import enhance_color

def test_color_detected():
    rec = {"title": "Zapatos deportivos color black edición limitada"}
    out = enhance_color(rec.copy())
    assert out["color"] == "black"

def test_color_no_change_when_not_found():
    rec = {"title": "Producto sin color claro"}
    out = enhance_color(rec.copy())
    # Should not add color if none detected
    assert out == rec
