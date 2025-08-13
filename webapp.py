from flask import Flask, request, render_template_string, send_file, redirect, url_for
import os
import tempfile
import shutil
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = tempfile.gettempdir()

HTML = '''
<!doctype html>
<title>ML Extractor Web UI</title>
<h2>ML Extractor - Upload & Extract</h2>
<form method=post enctype=multipart/form-data>
  <label>Input file:</label>
  <input type=file name=input_file required><br><br>
  <label>Config file:</label>
  <select name=config_file>
    {% for config in configs %}
      <option value="{{ config }}">{{ config }}</option>
    {% endfor %}
  </select><br><br>
  <input type=submit value=Extract>
</form>
{% if output_url %}
  <h3>Extraction complete!</h3>
  <a href="{{ output_url }}">Download output file</a>
{% endif %}
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    configs = [f for f in os.listdir('config') if f.endswith('.yaml')]
    output_url = None
    if request.method == 'POST':
        input_file = request.files['input_file']
        config_file = request.form['config_file']
        input_path = os.path.join(UPLOAD_FOLDER, input_file.filename)
        output_path = os.path.join(UPLOAD_FOLDER, f'output_{input_file.filename}')
        input_file.save(input_path)
        config_path = os.path.join('config', config_file)
        # Run the extractor
        cmd = [
            'python3', 'main.py',
            input_path, output_path,
            '--config', config_path
        ]
        subprocess.run(cmd, check=True)
        output_url = url_for('download_file', filename=os.path.basename(output_path))
    return render_template_string(HTML, configs=configs, output_url=output_url)

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
