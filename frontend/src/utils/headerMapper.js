// Shared header -> logical field mapper
// Returns one of the logical keys expected by backend, or null if unknown
export function mapHeaderToLogical(hdr) {
  if (!hdr && hdr !== 0) return null;
  const s = String(hdr).trim().toLowerCase();

  // Normalize accents and remove extra punctuation for matching
  const normalize = (text) => text
    .normalize('NFD').replace(/\p{Diacritic}/gu, '')
    .replace(/[\s\_\-]+/g, ' ')
    .replace(/[\.:,\(\)\[\]]/g, '')
    .trim();

  const t = normalize(s);

  // Title / name
  if (/\b(titulo|title|nombre|name|producto|producto nombre|nombre producto|item name)\b/.test(t)) return 'title';

  // Price
  if (/\b(precio|price|valor|costo|cost|amount|precio unitario|precio final)\b/.test(t)) return 'price';

  // Currency (not a target field but sometimes present)
  if (/\b(moneda|currency|ars|usd|brl)\b/.test(t)) return 'currency';

  // Stock / quantity
  if (/\b(stock|cantidad|qty|quantity|unidades|existencia|disponible)\b/.test(t)) return 'stock';

  // SKU / code / reference
  if (/\b(sku|codigo|codigo sku|cod|ref|referencia|id producto)\b/.test(t)) return 'sku';

  // Images
  if (/\b(imagen(es)?|image(s)?|foto(s)?|picture(s)?|imagen principal|url imagen)\b/.test(t)) return 'images';

  // Description
  if (/\b(descri(c|c)ion|description|detalle|detalles|desc)\b/.test(t)) return 'description';

  // Condition
  if (/\b(condicion|condicion del producto|condition|estado)\b/.test(t)) return 'condition';

  // Shipping / fulfillment
  if (/\b(envio|envio gratis|envio_gratis|shipping|fulfillment|fulfillment_type)\b/.test(t)) return 'shipping';

  // Category
  if (/\b(categoria|categoria padre|category|cat)\b/.test(t)) return 'category';

  // Brand / model
  if (/\b(marca|brand)\b/.test(t)) return 'brand';
  if (/\b(modelo|model)\b/.test(t)) return 'model';

  // Weight / dimensions
  if (/\b(peso|weight)\b/.test(t)) return 'weight';
  if (/\b(dimens|alto|ancho|largo|dimension|dimensions)\b/.test(t)) return 'dimensions';

  // Warranty
  if (/\b(garantia|warranty)\b/.test(t)) return 'warranty';

  // Default fallback: look for product_x style suffixes
  if (/\b(producto?_?titulo|product_?title|product_?name)\b/.test(t)) return 'title';
  if (/\b(producto?_?precio|product_?price)\b/.test(t)) return 'price';
  if (/\b(producto?_?stock|product_?stock)\b/.test(t)) return 'stock';

  return null;
}

export default mapHeaderToLogical;
