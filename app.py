
from flask import Flask, request, jsonify
from resumeparse import resumeparse
from flask_cors import CORS
import io
import aspose.words as aw
import os
import re
import docx2txt
from datetime import datetime
from werkzeug.utils import secure_filename

#from io import BytesIO

app = Flask(_name_)
CORS(app, resources={r"/resumeparse": {"origins": "http://localhost:3000"}})

class ResumeParser:
    @staticmethod
    def parse_resume(resume_file_path, count, count2):
        print("54")
        parser_obj = resumeparse()
        parsed_resume_data = parser_obj.read_file(resume_file_path, count, count2)
        print(parsed_resume_data, "99")
        return parsed_resume_data

@app.route('/resumeparse', methods=['POST'])
def parse_resume():
    print("Received a request to parse resume")
    try:
        is_folder_upload = request.form.get('isFolderUpload', False)
        count = 0
        count2 = 0
        if is_folder_upload:
            # Handle folder upload
            uploaded_files = request.files.getlist('resumes[]')
            parsed_resume_data_list = []
            
            # Process each file in the folder
            for resume_file in uploaded_files:
                
                resume_file_path = new_filename(secure_filename(resume_file.filename), resume_file)
                resume_file.save(resume_file_path)
                parsed_resume_data = ResumeParser.parse_resume(resume_file_path, count, count2)
                print(parsed_resume_data['row_newfile'], "122")
                count = parsed_resume_data['row_newfile']
                count2 = parsed_resume_data['row_oldfile']
                os.remove(resume_file_path)
                parsed_resume_data_list.append(parsed_resume_data)
                # Process parsed_resume_data as needed

            return jsonify({
             'newcount': int(count),
             'oldcount': int(count2)
             })

        else:
            uploaded_file = request.files.get('resumes[]')
            resume_file_path = new_filename(secure_filename(uploaded_file.filename), uploaded_file)
            uploaded_file.save(resume_file_path)
            parsed_resume_data = ResumeParser.parse_resume(resume_file_path)
            os.remove(resume_file_path)

            return jsonify(parsed_resume_data)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)})

def new_filename(org_filename, file):
    time = datetime.now()
    timestamp = time.strftime("%Y%m%d%H%M%S%f")
    unique_filename = f"{timestamp}_{org_filename}"
    return secure_filename(unique_filename)
@app.route('/greet', methods=['POST'])
def greet_user():
    print("hii")
    return jsonify({'message':'hello'})


if _name_ == '_main_':
    app.run(debug=True)


