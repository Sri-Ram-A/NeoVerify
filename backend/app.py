
from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/explore')
def explore():
    return render_template('upload.html')

@app.route('/process', methods=['POST'])
def process_upload():
    results = {}
    # Handle file uploads
    file_types = ['image', 'video', 'audio', 'text']
    for file_type in file_types:
        if file_type in request.files and request.files[file_type].filename:
            file = request.files[file_type]
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            results[file_type] = file_path
        else:
            results[file_type] = "No file uploaded"
    
    # Handle direct text entry (alternative to file upload)
    user_text = request.form.get('user-text', '')
    if user_text:
        results['text_entry'] = user_text
    else:
        results['text_entry'] = "No text entered"
    
    # Handle URL input
    url = request.form.get('url', '')
    results['url'] = url if url else "No URL provided"

    return render_template('upload.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
