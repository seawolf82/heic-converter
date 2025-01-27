from flask import Flask, request, render_template, jsonify, send_file
from pillow_heif import register_heif_opener
import pillow_heif
from PIL import Image
import os
import zipfile
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
register_heif_opener()

UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

conversion_status = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    uploaded_files = []
    
    for file in files:
        if file.filename:
            filename = secure_filename(file.filename)
            if filename.lower().endswith('.heic'):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                uploaded_files.append(filename)
                conversion_status[filename] = 'pending'
    
    return jsonify({
        'message': f'Uploaded {len(uploaded_files)} files',
        'files': uploaded_files
    })

@app.route('/convert', methods=['POST'])
def convert_files():
    files = request.json.get('files', [])
    
    for filename in files:
        try:
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            output_filename = os.path.splitext(filename)[0] + '.jpg'
            output_path = os.path.join(CONVERTED_FOLDER, output_filename)
            
            conversion_status[filename] = 'converting'
            
            heif_file = pillow_heif.read_heif(input_path)
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
            )
            image.save(output_path, 'JPEG')
            
            conversion_status[filename] = 'completed'
            
        except Exception as e:
            conversion_status[filename] = 'error'
            print(f"Error converting {filename}: {str(e)}")
    
    return jsonify({'status': 'success'})

@app.route('/status')
def get_status():
    return jsonify(conversion_status)

@app.route('/download')
def download_files():
    zip_path = os.path.join(CONVERTED_FOLDER, 'converted_images.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in os.listdir(CONVERTED_FOLDER):
            if filename.endswith('.jpg'):
                file_path = os.path.join(CONVERTED_FOLDER, filename)
                zipf.write(file_path, filename)
    
    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

