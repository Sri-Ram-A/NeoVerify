
from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from fighter import ClaimFighter
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
    file_types = ['image', 'video', 'audio']
    for file_type in file_types:
        if file_type in request.files and request.files[file_type].filename:
            file = request.files[file_type]
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            results[file_type] = file_path
        else:
            results[file_type] = None
    
    # Handle direct text entry (alternative to file upload)
    user_text = request.form.get('user-text', '')
    if user_text:
        results['text'] = user_text
    else:
        results['text'] = None
    # Handle URL input
    url = request.form.get('url', '')
    results['url'] = url if url else None
    print(results)
    fighter = ClaimFighter()
    fighter.run(results)
    return render_template('upload.html', results=results)

@app.route('/knowledge_graph')
def knowledge_graph():
    import json
    try:
        with open("/workspaces/fantom_code/backend/news_verification/output.json", 'r', encoding='utf-8') as file:
            output = json.load(file)
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    if output:
        print("Successfully loaded JSON data into dictionary")
    return render_template('knowledge_graph.html',output=output)

@app.route('/chat')
def chat():
    import json
    try:
        with open("/workspaces/fantom_code/backend/news_verification/output.json", 'r', encoding='utf-8') as file:
            output = json.load(file)
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    if output:
        print("Successfully loaded JSON data into dictionary")
    return render_template('chat.html',output=output)

if __name__ == '__main__':
    app.run(debug=True)
