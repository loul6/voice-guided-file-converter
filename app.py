from flask import Flask, request, send_file, render_template, jsonify
from services.converter import perform_conversion
from services.voice import generate_speech
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    file = request.files['file']
    target_format = request.form['target_format']
    converted, filename = perform_conversion(io.BytesIO(file.read()), file.filename, target_format)
    return send_file(converted, as_attachment=True, download_name=filename)

@app.route('/speak', methods=['POST'])
def speak():
    text = request.json.get('text')
    data = generate_speech(text)
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
