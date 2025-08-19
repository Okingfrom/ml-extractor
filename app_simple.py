#!/usr/bin/env python3
"""
Minimal fallback Flask app (simple UI) for quick browsing and testing.
This intentionally avoids heavy libraries and only requires Flask.
"""
from flask import Flask, render_template_string, request, redirect, url_for
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

HTML = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Mercado Libre Bulk Mapper (Simple)</title>
  <style>
    :root{
      --ml-yellow:#FFE600;
      --ml-yellow-dark:#FFD000;
      --ml-blue:#3483FA;
      --bg:#ffffff;
      --text:#222;
      --muted:#666;
    }
    html,body{height:100%;margin:0;padding:0;background:var(--bg);color:var(--text);font-family:Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial}
    .page{min-height:100%;display:flex;align-items:flex-start;justify-content:center;padding:24px}
    .card{width:100%;max-width:920px;background:#fff;border-radius:12px;box-shadow:0 6px 18px rgba(16,24,40,0.06);padding:20px}
    header{display:flex;align-items:center;gap:16px}
    .logo{width:160px;height:48px;display:inline-block}
    h1{font-size:20px;margin:0}
    p.lead{color:var(--muted);margin:6px 0 18px}
    form{display:flex;flex-direction:column;gap:12px}
    label{font-weight:600;font-size:13px}
    input[type=file], input[type=text]{width:100%;padding:10px;border:1px solid #e6e6e6;border-radius:8px}
    .btn{background:linear-gradient(90deg,var(--ml-blue),#2b73d1);color:#fff;padding:10px 16px;border:none;border-radius:8px;font-weight:600;cursor:pointer}
    .note{font-size:13px;color:var(--muted)}
    @media (max-width:600px){.logo{width:120px;height:36px}.card{padding:16px}}
  </style>
</head>
<body>
  <div class="page">
    <div class="card">
      <header>
        <!-- Inline professional SVG logo (Mercado Libre color accents) -->
        <div class="logo" aria-hidden="true">
          <svg viewBox="0 0 512 128" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
            <defs>
              <linearGradient id="g1" x1="0%" x2="100%" y1="0%" y2="0%">
                <stop offset="0%" stop-color="#FFE600"/>
                <stop offset="100%" stop-color="#FFD000"/>
              </linearGradient>
            </defs>
            <rect width="512" height="128" rx="16" fill="transparent"/>
            <g transform="translate(14,12)">
              <circle cx="40" cy="40" r="32" fill="var(--ml-blue)" />
              <path d="M28 34c2-6 12-12 22-6 6 4 8 12 6 18-2 6-8 10-14 10-8 0-14-8-14-22z" fill="url(#g1)" transform="translate(6,6) scale(0.9)"/>
            </g>
            <g transform="translate(120,42)">
              <text x="0" y="0" font-family="Inter, Arial, sans-serif" font-weight="700" font-size="22" fill="var(--text)">Mercado Libre</text>
              <text x="0" y="22" font-family="Inter, Arial, sans-serif" font-weight="600" font-size="14" fill="#666">Bulk Mapper</text>
            </g>
          </svg>
        </div>
        <div>
          <h1>Mercado Libre Bulk Mapper</h1>
          <p class="lead">Simple, fast uploads for testing — lightweight and mobile-friendly.</p>
        </div>
      </header>

      {% if message %}
        <div class="note">{{ message }}</div>
      {% endif %}

      <form method="post" enctype="multipart/form-data">
        <div>
          <label>Template (.xlsx)</label>
          <input type="file" name="template" accept=".xlsx">
        </div>
        <div>
          <label>Product Data (.xlsx/.csv/.txt)</label>
          <input type="file" name="content" accept=".xlsx,.xls,.csv,.txt">
        </div>
        <div>
          <label>Mapping Config Path</label>
          <input type="text" name="config_path" value="config/mapping.yaml">
        </div>
        <div>
          <button class="btn" type="submit">Process Files</button>
        </div>
      </form>

      <hr>
      <p class="note">Files uploaded are kept in <code>uploads/</code>. This simple UI avoids heavy processing and is intended for testing and layout review.</p>
    </div>
  </div>
</body>
</html>
'''


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Save uploads for manual testing; no heavy processing here
        tf = request.files.get('template')
        cf = request.files.get('content')
        if tf:
            tf.save(os.path.join(app.config['UPLOAD_FOLDER'], tf.filename))
        if cf:
            cf.save(os.path.join(app.config['UPLOAD_FOLDER'], cf.filename))
        return render_template_string(HTML, message='Files uploaded to uploads/ (no processing in simple UI)')
    return render_template_string(HTML)


if __name__ == '__main__':
    print('Starting simple UI at http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)

