# app.py
from flask import Flask, render_template, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
from ocr_module import OCRPDFExtractor
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

extractor = OCRPDFExtractor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'File must be a PDF'}), 400

    try:
        result = extractor.extract_lines(file)
        
        # Save result to file
        output_path = os.path.join(
            app.config['UPLOAD_FOLDER'], 
            secure_filename(f"{file.filename}_result.json")
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.__dict__, f, indent=2, ensure_ascii=False)
        
        return jsonify(result.__dict__)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)