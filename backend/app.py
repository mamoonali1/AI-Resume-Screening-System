import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from parser import extract_text_from_file
from analyzer import analyze_resumes

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allows cross-origin requests from frontend

@app.route('/screen', methods=['POST'])
def screen_resumes():
    if 'resumes' not in request.files or 'job_description' not in request.form:
        return jsonify({"error": "Missing required data (resumes or job_description)"}), 400

    files = request.files.getlist('resumes')
    job_description = request.form.get('job_description')
    scale = int(request.form.get('scale', 100))
    
    # Extract structural configuration filters
    filters = {
        "education": request.form.get('filter_education', ''),
        "min_exp": int(request.form.get('filter_min_exp')) if request.form.get('filter_min_exp') else None,
        "max_exp": int(request.form.get('filter_max_exp')) if request.form.get('filter_max_exp') else None,
        "universities": request.form.get('filter_universities', '').split(',') if request.form.get('filter_universities') else []
    }

    # Extract text content from documents
    raw_resumes = []
    for file in files:
        if file.filename != '':
            try:
                text = extract_text_from_file(file)
                raw_resumes.append({"filename": file.filename, "text": text})
            except Exception as e:
                print(f"Error reading file {file.filename}: {e}")

    if not raw_resumes:
        return jsonify({"error": "No valid text could be extracted from uploaded documents"}), 400

    # Execute main analysis pipeline
    shortlisted = analyze_resumes(raw_resumes, job_description, filters, scale)
    
    return jsonify({"shortlisted": shortlisted})

if __name__ == '__main__':
    app.run(debug=True, port=5000)