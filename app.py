from flask import Flask, request, jsonify
from resumeparse import resumeparse
from flask_cors import CORS
import io
import aspose.words as aw
import os
import re
import docx2txt
#from io import BytesIO

app = Flask(__name__)
CORS(app, resources={r"/resumeparse": {"origins": "http://localhost:3000"}})

class ResumeParser:
    @staticmethod
    def parse_resume(resume_file_path, docx_parser="tika"):
        parser_obj = resumeparse()
        parsed_resume_data = parser_obj.read_file(resume_file_path, docx_parser)
        return parsed_resume_data

@app.route('/resumeparse', methods=['POST'])
def parse_resume():
    print("Received a request to parse resume")
    try:
        # Get the resume file from the request
        
        
        resume_file = request.files['resume']
        docx_parser = request.form.get('docx_parser', 'tika')
        
        
        filename = resume_file.filename

        # Save the file to a temporary location
        if filename.lower().endswith('docx'):
            
            resume_file_path = 'True_Talent.docx'
        elif filename.lower().endswith('pdf'):
           
            resume_file_path = 'True_Talent.pdf'
        elif filename.lower().endswith('doc'):
            
            resume_file_path = 'True_Talent.doc'
            
        
        resume_file.save(resume_file_path)

        # Parse the resume
        parsed_resume_data = ResumeParser.parse_resume(resume_file_path, docx_parser)

        return jsonify(parsed_resume_data)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)})
@app.route('/greet', methods=['POST'])
def greet_user():
    try:
        data = request.get_json()
        first_name = data.get('first_name', 'User')

        greeting = f"Hello {first_name}, please fill in the details."
        return jsonify({'greeting': greeting})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)

