# %%writefile /content/resume_parser/resume_parser/resumeparse.py
# !apt-get install python-dev libxml2-dev libxslt1-dev antiword unrtf poppler-resumeparse pstotext tesseract-ocr
# !sudo apt-get install libenchant1c2a


# !pip install tika
# !pip install docx2txt
# !pip install phonenumbers
# !pip install pyenchant
# !pip install stemming

from __future__ import division
import nltk
import aspose.words as aw

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('universal_tagset')
# nltk.download('maxent_ne_chunker')
# nltk.download('stopwords')
# nltk.download('wordnet')
# nltk.download('brown')

import re
import os
import shutil
from datetime import date

import nltk
import docx2txt
import pandas as pd

import phonenumbers
import pdfplumber

import logging

import spacy
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher


import sys
import operator
import string
import nltk
from stemming.porter2 import stem
import mysql.connector

# load pre-trained model
base_path = os.path.dirname(_file_)


nlp = spacy.load('en_core_web_sm')

custom_nlp2 = spacy.load(os.path.join(base_path,"degree","model"))
custom_nlp3 = spacy.load(os.path.join(base_path,"company_working","model"))

# initialize matcher with a vocab
matcher = Matcher(nlp.vocab)

# The below 6 line code is to extract designation
file = os.path.join(base_path,"titles_combined.txt")
file = open(file, "r", encoding='utf-8')
designation = [line.strip().lower() for line in file]
designitionmatcher = PhraseMatcher(nlp.vocab)
patterns = [nlp.make_doc(text) for text in designation if len(nlp.make_doc(text)) < 10]
designitionmatcher.add("Job title", None, *patterns)
                        
# The below 6 line code is to extract skills
file = os.path.join(base_path,"LINKEDIN_SKILLS_ORIGINAL.txt") 
file = open(file, "r", encoding='utf-8')    
skill = [line.strip().lower() for line in file]
skillsmatcher = PhraseMatcher(nlp.vocab)
patterns = [nlp.make_doc(text) for text in skill if len(nlp.make_doc(text)) < 10]
skillsmatcher.add("Job title", None, *patterns)


class resumeparse(object):
    def extract_projects(text):
        """
        Extract project details from the given text.
        You may need to adapt this function based on how project details are presented in your resume.

        Parameters:
        - text (str): The text containing information about projects.

        Returns:
        - List of project details.
        """
        projects = []
        project_starts = re.finditer(r'Project[^\w\n](\w[^\n])', text, re.IGNORECASE)
        
        for start_match in project_starts:
            project_start = start_match.group(1)
            project_end_match = re.search(r'(?:(?:Project|Objective|Work and Employment|Education and Training|Skills|Accomplishments|Misc):|$)', project_start, re.IGNORECASE)
            
            if project_end_match:
                project_end_index = project_end_match.start()
                project_details = project_start[:project_end_index].strip()
                projects.append(project_details)

        return projects
       
    objective = (
        'career goal',
        'objective',
        'career objective',
        'employment objective',
        'professional objective',        
        'career summary',
        'professional summary',
        'summary of qualifications',
        'summary',
        # 'digital'
    )

    work_and_employment = (
        'career profile',
        'employment history',
        'work history',
        'work experience',
        'experience',
        'professional experience',
        'professional background',
        'additional experience',
        'career related experience',
        'related experience',
        'programming experience',
        'freelance',
        'freelance experience',
        'army experience',
        'military experience',
        'military background',
    )

    education_and_training = (
        'academic background',
        'academic experience',
        'programs',
        'courses',
        'related courses',
        'education',
        'qualifications',
        'educational background',
        'educational qualifications',
        'educational training',
        'education and training',
        'training',
        'academic training',
        'professional training',
        'course project experience',
        'related course projects',
        'internship experience',
        'internships',
        'apprenticeships',
        'college activities',
        'certifications',
        'special training',
    )

    skills_header = (
        'credentials',
        'areas of experience',
        'areas of expertise',
        'areas of knowledge',
        'skills',
        "other skills",
        "other abilities",
        'career related skills',
        'professional skills',
        'specialized skills',
        'technical skills',
        'computer skills',
        'personal skills',
        'computer knowledge',        
        'technologies',
        'technical experience',
        'proficiencies',
        'languages',
        'language competencies and skills',
        'programming languages',
        'competencies'
    )

    misc = (
        'activities and honors',
        'activities',
        'affiliations',
        'professional affiliations',
        'associations',
        'professional associations',
        'memberships',
        'professional memberships',
        'athletic involvement',
        'community involvement',
        'refere',
        'civic activities',
        'extra-Curricular activities',
        'professional activities',
        'volunteer work',
        'volunteer experience',
        'additional information',
        'interests'
    )

    accomplishments = (
        'achievement',
        'licenses',
        'presentations',
        'conference presentations',
        'conventions',
        'dissertations',
        'exhibits',
        'papers',
        'publications',
        'professional publications',
        'research',
        'research grants',
        'project',
        'research projects',
        'personal projects',
        'current research interests',
        'thesis',
        'theses',
    )
       

           
    def convert_docx_to_txt(docx_file):
        """
            A utility function to convert a Microsoft docx files to raw text.

            This code is largely borrowed from existing solutions, and does not match the style of the rest of this repo.
            :param docx_file: docx file with gets uploaded by the user
            :type docx_file: InMemoryUploadedFile
            :return: The text contents of the docx file
            :rtype: str
        """
        try:
            print(docx_file)
            text = docx2txt.process(docx_file)  # Extract text from docx file
            print("242")
            # txt_file = "./True_Talent.txt"

            # with open(txt_path, 'w', encoding='utf-8') as txt_file:
            #     txt_file.write(text)
            
            clean_text = text.replace("\r", "\n").replace("\t", " ")  # Normalize text blob
            print("243")
            resume_lines = clean_text.splitlines()  # Split text blob into individual lines
            print("244")
            resume_lines = [re.sub('\s+', ' ', line.strip()) for line in resume_lines if line.strip()]  # Remove empty strings and whitespaces
            
            print(resume_lines)

            return resume_lines, text
        except KeyError:
            print('suma')
            
            text = textract.process(docx_file)
            text = text.decode("utf-8")
            clean_text = text.replace("\r", "\n").replace("\t", " ")  # Normalize text blob
            resume_lines = clean_text.splitlines()  # Split text blob into individual lines
            resume_lines = [re.sub('\s+', ' ', line.strip()) for line in resume_lines if line.strip()]  # Remove empty strings and whitespaces
            return resume_lines, text
        try:
            clean_text = re.sub(r'\n+', '\n', text)
            clean_text = clean_text.replace("\r", "\n").replace("\t", " ")  # Normalize text blob
            resume_lines = clean_text.splitlines()  # Split text blob into individual lines
            resume_lines = [re.sub('\s+', ' ', line.strip()) for line in resume_lines if
                            line.strip()]  # Remove empty strings and whitespaces
            return resume_lines, text
        except Exception as e:
            logging.error('Error in docx file:: ' + str(e))
            return [], " "

    def convert_doc_to_txt(doc_file):
        try:
            print(doc_file)
            doc = aw.Document(doc_file)
            doc.save('True_Talent(doc_to_docx).docx')
            print("hello")
            text = docx2txt.process('True_Talent(doc_to_docx).docx')  # Extract text from docx file
            print("241")
            resume_lines = ""
            clean_text = text.replace("\r", "\n").replace("\t", " ")  # Normalize text blob            print("242")
            resume_lines = clean_text.splitlines()  # Split text blob into individual lines
            resume_lines = [re.sub('\s+', ' ', line.strip()) for line in resume_lines if line.strip()]  # Remove empty strings and whitespaces
            print('246')
            resume_lines = resume_lines[1:]
            resume_lines = resume_lines[:-3]
            print(resume_lines)
        
            return resume_lines, text
        except Exception as e:
            logging.error('Error in doc file:: ' + str(e))
            return [], " "




    def convert_pdf_to_txt(pdf_file):
        """
        A utility function to convert a machine-readable PDF to raw text.

        This code is largely borrowed from existing solutions, and does not match the style of the rest of this repo.
        :param input_pdf_path: Path to the .pdf file which should be converted
        :type input_pdf_path: str
        :return: The text contents of the pdf
        :rtype: str
        """
        # try:
        #     #PDFMiner boilerplate
        #     pdf = pdfplumber.open(pdf_file)
        #     full_string= ""
        #     for page in pdf.pages:
        #       full_string += page.extract_text() + "\n"
        #     pdf.close()

            
        # try:

        #     raw_text = parser.from_file(pdf_file, service='text')['content']
        #     print("in try")
        # except RuntimeError as e:  
        try:
            print("in excpt")          
            # logging.error('Error in tika installation:: ' + str(e))
            # logging.error('--------------------------')
            # logging.error('Install java for better result ')
            pdf = pdfplumber.open(pdf_file)
            raw_text= ""
            for page in pdf.pages:
                raw_text += page.extract_text() + "\n"
                
            pdf.close()  
            print('out except 313')              
        except Exception as e:
            logging.error('Error in docx file:: ' + str(e))
            return [], " "
        try:
            full_string = re.sub(r'\n+', '\n', raw_text)
            full_string = full_string.replace("\r", "\n")
            full_string = full_string.replace("\t", " ")

            # Remove awkward LaTeX bullet characters

            full_string = re.sub(r"\uf0b7", " ", full_string)
            full_string = re.sub(r"\(cid:\d{0,2}\)", " ", full_string)
            full_string = re.sub(r'• ', " ", full_string)

            # Split text blob into individual lines
            resume_lines = full_string.splitlines(True)

            # Remove empty strings and whitespaces
            resume_lines = [re.sub('\s+', ' ', line.strip()) for line in resume_lines if line.strip()]
            print(resume_lines)
            return resume_lines, raw_text
        except Exception as e:
            logging.error('Error in docx file:: ' + str(e))
            return [], " "
            
    def find_segment_indices(string_to_search, resume_segments, resume_indices):
        for i, line in enumerate(string_to_search):

            if line[0].islower():
                continue

            header = line.lower()

            if [o for o in resumeparse.objective if header.startswith(o)]:
                try:
                    resume_segments['objective'][header]
                except:
                    resume_indices.append(i)
                    header = [o for o in resumeparse.objective if header.startswith(o)][0]
                    resume_segments['objective'][header] = i
            elif [w for w in resumeparse.work_and_employment if header.startswith(w)]:
                try:
                    resume_segments['work_and_employment'][header]
                except:
                    resume_indices.append(i)
                    header = [w for w in resumeparse.work_and_employment if header.startswith(w)][0]
                    resume_segments['work_and_employment'][header] = i
            elif [e for e in resumeparse.education_and_training if header.startswith(e)]:
                try:
                    resume_segments['education_and_training'][header]
                except:
                    resume_indices.append(i)
                    header = [e for e in resumeparse.education_and_training if header.startswith(e)][0]
                    resume_segments['education_and_training'][header] = i
            elif [s for s in resumeparse.skills_header if header.startswith(s)]:
                try:
                    resume_segments['skills'][header]
                except:
                    resume_indices.append(i)
                    header = [s for s in resumeparse.skills_header if header.startswith(s)][0]
                    resume_segments['skills'][header] = i
            elif [m for m in resumeparse.misc if header.startswith(m)]:
                try:
                    resume_segments['misc'][header]
                except:
                    resume_indices.append(i)
                    header = [m for m in resumeparse.misc if header.startswith(m)][0]
                    resume_segments['misc'][header] = i
            elif [a for a in resumeparse.accomplishments if header.startswith(a)]:
                try:
                    resume_segments['accomplishments'][header]
                except:
                    resume_indices.append(i)
                    header = [a for a in resumeparse.accomplishments if header.startswith(a)][0]
                    resume_segments['accomplishments'][header] = i

    def slice_segments(string_to_search, resume_segments, resume_indices):
        resume_segments['contact_info'] = string_to_search[:resume_indices[0]]

        for section, value in resume_segments.items():
            if section == 'contact_info':
                continue

            for sub_section, start_idx in value.items():
                end_idx = len(string_to_search)
                if (resume_indices.index(start_idx) + 1) != len(resume_indices):
                    end_idx = resume_indices[resume_indices.index(start_idx) + 1]

                resume_segments[section][sub_section] = string_to_search[start_idx:end_idx]

    def segment(string_to_search):
        resume_segments = {
            'objective': {},
            'work_and_employment': {},
            'education_and_training': {},
            'skills': {},
            'accomplishments': {},
            'misc': {}
        }

        resume_indices = []

        resumeparse.find_segment_indices(string_to_search, resume_segments, resume_indices)
        if len(resume_indices) != 0:
            resumeparse.slice_segments(string_to_search, resume_segments, resume_indices)
        else:
            resume_segments['contact_info'] = []

        return resume_segments

    # def calculate_experience(resume_text):
        
    #     #
    #     # def get_month_index(month):
    #     #   month_dict = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6, 'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12}
    #     #   return month_dict[month.lower()]
    #     # print(resume_text)
    #     # print("*"*100)
    #     def correct_year(result):
    #         if len(result) < 2:
    #             if int(result) > int(str(date.today().year)[-2:]):
    #                 result = str(int(str(date.today().year)[:-2]) - 1) + result
    #             else:
    #                 result = str(date.today().year)[:-2] + result
    #         return result

    #     # try:
    #     experience = 0
    #     start_month = -1
    #     start_year = -1
    #     end_month = -1
    #     end_year = -1

    #     not_alpha_numeric = r'[^a-zA-Z\d]'
    #     number = r'(\d{2})'

    #     months_num = r'(01)|(02)|(03)|(04)|(05)|(06)|(07)|(08)|(09)|(10)|(11)|(12)'
    #     months_short = r'(jan)|(feb)|(mar)|(apr)|(may)|(jun)|(jul)|(aug)|(sep)|(oct)|(nov)|(dec)'
    #     months_long = r'(january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december)'
    #     month = r'(' + months_num + r'|' + months_short + r'|' + months_long + r')'
    #     regex_year = r'((20|19)(\d{2})|(\d{2}))'
    #     year = regex_year
    #     start_date = month + not_alpha_numeric + r"?" + year
        
    #     # end_date = r'((' + number + r'?' + not_alpha_numeric + r"?" + number + not_alpha_numeric + r"?" + year + r')|(present|current))'
    #     end_date = r'((' + number + r'?' + not_alpha_numeric + r"?" + month + not_alpha_numeric + r"?" + year + r')|(present|current|till date|today))'
    #     longer_year = r"((20|19)(\d{2}))"
    #     year_range = longer_year + r"(" + not_alpha_numeric + r"{1,4}|(\s*to\s*))" + r'(' + longer_year + r'|(present|current|till date|today))'
    #     date_range = r"(" + start_date + r"(" + not_alpha_numeric + r"{1,4}|(\s*to\s*))" + end_date + r")|(" + year_range + r")"

        
    #     regular_expression = re.compile(date_range, re.IGNORECASE)
        
    #     regex_result = re.search(regular_expression, resume_text)
        
    #     while regex_result:
          
    #       try:
    #         date_range = regex_result.group()
    #         # print(date_range)
    #         # print("*"*100)
    #         try:
              
    #             year_range_find = re.compile(year_range, re.IGNORECASE)
    #             year_range_find = re.search(year_range_find, date_range)
    #             # print("year_range_find",year_range_find.group())
                                
    #             # replace = re.compile(r"(" + not_alpha_numeric + r"{1,4}|(\s*to\s*))", re.IGNORECASE)
    #             replace = re.compile(r"((\s*to\s*)|" + not_alpha_numeric + r"{1,4})", re.IGNORECASE)
    #             replace = re.search(replace, year_range_find.group().strip())
    #             # print(replace.group())
    #             # print(year_range_find.group().strip().split(replace.group()))
    #             start_year_result, end_year_result = year_range_find.group().strip().split(replace.group())
    #             # print(start_year_result, end_year_result)
    #             # print("*"*100)
    #             start_year_result = int(correct_year(start_year_result))
    #             if (end_year_result.lower().find('present') != -1 or 
    #                 end_year_result.lower().find('current') != -1 or 
    #                 end_year_result.lower().find('till date') != -1 or 
    #                 end_year_result.lower().find('today') != -1): 
    #                 end_month = date.today().month  # current month
    #                 end_year_result = date.today().year  # current year
    #             else:
    #                 end_year_result = int(correct_year(end_year_result))


    #         except Exception as e:
    #             # logging.error(str(e))
    #             start_date_find = re.compile(start_date, re.IGNORECASE)
    #             start_date_find = re.search(start_date_find, date_range)

    #             non_alpha = re.compile(not_alpha_numeric, re.IGNORECASE)
    #             non_alpha_find = re.search(non_alpha, start_date_find.group().strip())

    #             replace = re.compile(start_date + r"(" + not_alpha_numeric + r"{1,4}|(\s*to\s*))", re.IGNORECASE)
    #             replace = re.search(replace, date_range)
    #             date_range = date_range[replace.end():]
        
    #             start_year_result = start_date_find.group().strip().split(non_alpha_find.group())[-1]

    #             # if len(start_year_result)<2:
    #             #   if int(start_year_result) > int(str(date.today().year)[-2:]):
    #             #     start_year_result = str(int(str(date.today().year)[:-2]) - 1 )+start_year_result
    #             #   else:
    #             #     start_year_result = str(date.today().year)[:-2]+start_year_result
    #             # start_year_result = int(start_year_result)
    #             start_year_result = int(correct_year(start_year_result))

    #             if date_range.lower().find('present') != -1 or date_range.lower().find('current') != -1:
    #                 end_month = date.today().month  # current month
    #                 end_year_result = date.today().year  # current year
    #             else:
    #                 end_date_find = re.compile(end_date, re.IGNORECASE)
    #                 end_date_find = re.search(end_date_find, date_range)

    #                 end_year_result = end_date_find.group().strip().split(non_alpha_find.group())[-1]

    #                 # if len(end_year_result)<2:
    #                 #   if int(end_year_result) > int(str(date.today().year)[-2:]):
    #                 #     end_year_result = str(int(str(date.today().year)[:-2]) - 1 )+end_year_result
    #                 #   else:
    #                 #     end_year_result = str(date.today().year)[:-2]+end_year_result
    #                 # end_year_result = int(end_year_result)
    #                 try:
    #                   end_year_result = int(correct_year(end_year_result))
    #                 except Exception as e:
    #                   logging.error(str(e))
    #                   end_year_result = int(re.search("\d+",correct_year(end_year_result)).group())

    #         if (start_year == -1) or (start_year_result <= start_year):
    #             start_year = start_year_result
    #         if (end_year == -1) or (end_year_result >= end_year):
    #             end_year = end_year_result

    #         resume_text = resume_text[regex_result.end():].strip()
    #         regex_result = re.search(regular_expression, resume_text)
    #       except Exception as e:
    #         logging.error(str(e))
    #         resume_text = resume_text[regex_result.end():].strip()
    #         regex_result = re.search(regular_expression, resume_text)
            
    #     return end_year - start_year  # Use the obtained month attribute

    # except Exception as exception_instance:
    #   logging.error('Issue calculating experience: '+str(exception_instance))
    #   return None

    # def get_experience(resume_segments):
    #     total_exp = 0
    #     if len(resume_segments['work_and_employment'].keys()):
    #         text = ""
    #         for key, values in resume_segments['work_and_employment'].items():
    #             text += " ".join(values) + " "
    #         total_exp = resumeparse.calculate_experience(text)
    #         return total_exp, text
    #     else:
    #         text = ""
    #         for key in resume_segments.keys():
    #             if key != 'education_and_training':
    #                 if key == 'contact_info':
    #                     text += " ".join(resume_segments[key]) + " "
    #                 else:
    #                     for key_inner, value in resume_segments[key].items():
    #                         text += " ".join(value) + " "
    #         total_exp = resumeparse.calculate_experience(text)
    #         return total_exp, text
    #     return total_exp, " "

    def find_phone(text):
        try:
            return list(iter(phonenumbers.PhoneNumberMatcher(text, None)))[0].raw_string
        except:
            try:
                return re.search(
                    r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})',
                    text).group()
            except:
                return ""

    def extract_email(text):
        email = re.findall(r"([^@|\s]+@[^@]+\.[^@|\s]+)", text)
        if email:
            try:
                return email[0].split()[0].strip(';')
            except IndexError:
                return None

    # def extract_objective(text):
    #     objectives = []

    #     objective_terms = [
    #         'profile summary',
    #         'profile & strengths',
    #         'career objective',
    #         'employment objective',
    #         'professional objective',        
    #         'career summary',
    #         'work summary',
    #         'carrier summery',
    #         'programmer analyst',
    #         'professional summary',
    #         'summary of qualifications',
    #         'summary',
    #         'SUMMARY'
    #         'career goal',
    #         'objective',
    #         'PROFILE',
    #         'about me',
    #         'background',
    #     ]

    #     objective_pattern = '|'.join(map(re.escape, objective_terms))


    #     objective_starts = re.finditer(fr'({objective_pattern})[^\w\n](\w[^\n])', text, re.IGNORECASE)
        

        

        # for start_match in objective_starts:
        #     section_type = start_match.group(1)
        #     section_start = start_match.group(2)

            

        #     section_end_match = re.search(r'(?::|$)', section_start)
        #     if section_end_match:
        #         section_end_match1 = re.search(r'(?<=\. )(?::|$|SUMMARY|TECHNICAL SKILL|PROFESSIONAL|Education|EDUCATION|\bExperience\b|WORK EXPERIENCE|EXPERIENCE|Technical Skill|Skills|SKILL|SKILLS|Skill|Course|COURSE|Academic Qualification|\bCAREER TIMELINE\b)', section_start)
             
                        
        #         if section_end_match1:
        #             section_end_index = section_end_match1.start()
        #             section_details = section_start[:section_end_index].strip()
        #             objectives.append((section_type, section_details))

        #     else:
                
        #         section_end_match = re.search(r'(?<=\. )(?::|$|TECHNICAL SKILL|Education|EDUCATION|\bExperience\b|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|EXPERIENCE|Technical Skill|Skills|SKILL|SKILLS|Skill|Course|COURSE|Academic Qualification|\bCAREER TIMELINE\b)', section_start)
            

        #         if section_end_match:
        #             section_end_index = section_end_match.start()
        #             section_details = section_start[:section_end_index].strip()
        #             objectives.append((section_type, section_details))
                    



        # return objectives

    # def extract_full(resume_lines, full_text):
    #     # print(resume_lines, 679)
    #     print(full_text, 680)

    #     data = resume_lines

    #     if not full_text.strip():
    #         return ""


    #     else:
    #         mainframe_index = next((index for index, value in enumerate(data) if full_text in value), None)
    #         full_name = resume_lines[mainframe_index]
    #         return full_name
    #     # print(mainframe_info, "691")


        #=======
   
    # def extract_name(resume_text):
    #     nlp_text = nlp(resume_text)
    #     print(resume_text)

    #     # First name and Last name are always Proper Nouns
    #     # pattern_FML = [{'POS': 'PROPN', 'ENT_TYPE': 'PERSON', 'OP': '+'}]

    #     pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    #     matcher.add('NAME', None, pattern)

    #     matches = matcher(nlp_text)
    #     first_name = ""
    #     last_name = ""
    #     for match_id, start, end in matches:
    #         span = nlp_text[start:end]
    #         if not first_name:
    #             first_name = span.text
    #         else:
    #               last_name = span.text    
    #     if ' ' in first_name:
    #             first_name, last_name = first_name.split(' ', 1)
    #     return first_name, last_name
    #========


    # def extract_name(resume_text):
    #     nlp_text = nlp(resume_text)
    #     print(nlp_text)

    #     contains_software = 'sldba' in [token.text.lower() for token in nlp_text]

    #     print(contains_software, "728")

        

    #     pattern = [{'POS': 'PROPN'}]
    #     matcher.add('NAME', None, pattern)

    #     matches = matcher(nlp_text)

    #     avoid_words = ["sldba", "name", 'resume']

        

    #     for match_id, start, end in matches:
    #         span = nlp_text[start]
    #         if any(word.lower() in span.text.lower() for word in avoid_words):
    #             continue
            
    #         return span.text
    #     return ""

    # def extract_university(text, file):
    #     df = pd.read_csv(file, header=None)
    #     universities = [i.lower() for i in df[1]]
    #     college_name = []
    #     listex = universities
    #     listsearch = [text.lower()]

    #     for i in range(len(listex)):
    #         for ii in range(len(listsearch)):
                
    #             if re.findall(listex[i], re.sub(' +', ' ', listsearch[ii])):
                
    #                 college_name.append(listex[i])
        
    #     return college_name

    # def job_designition(text):
    #     job_titles = []
        
    #     __nlp = nlp(text.lower())
        
    #     matches = designitionmatcher(__nlp)
    #     for match_id, start, end in matches:
    #         span = __nlp[start:end]
    #         job_titles.append(span.text)
    #     return job_titles

    # def get_degree(text):
    #     doc = custom_nlp2(text)
    #     degree = []

    #     degree = [ent.text.replace("\n", " ") for ent in list(doc.ents) if ent.label_ == 'Degree']
    #     return list(dict.fromkeys(degree).keys())

    # def get_company_working(text):
    #     doc = custom_nlp3(text)
    #     degree = []

    #     degree = [ent.text.replace("\n", " ") for ent in list(doc.ents)]
    #     return list(dict.fromkeys(degree).keys())
    
    # def extract_skills(text):

    #     skills = []

    #     __nlp = nlp(text.lower())
    #     # Only run nlp.make_doc to speed things up

    #     matches = skillsmatcher(__nlp)
    #     for match_id, start, end in matches:
    #         span = __nlp[start:end]
    #         skills.append(span.text)
    #     skills = list(set(skills))
    #     return skills
    # def extract_location(text):
    #     nlp = spacy.load("en_core_web_sm")
    #     doc = nlp(text)

    #     locations = []
    #     for ent in doc.ents:
    #         if ent.label_ in ["GPE", "LOC"]:
    #             locations.append(ent.text)

    #     formatted_location = ', '.join(locations)  # Format as "village, city"
    
    #     if formatted_location.strip():
    #         return formatted_location.strip()
    #     else:
    #         return None
    
    
    # def extract_address(text):
    #     nlp = spacy.load("en_core_web_sm")
    #     doc = nlp(text)

    #     address_components = []
    #     for ent in doc.ents:
    #         if ent.label_ in ["GPE", "LOC"]:
    #             if ent.root.dep_ not in ['prep', 'pobj']:  # Exclude prepositions and objects
    #                 address_components.append(ent.text)

    #     formatted_address = ', '.join(address_components)  # Format as "village, city"

    #     if formatted_address.strip():
    #         return formatted_address.strip()
    #     else:
    #         return None
   
    
    
        
        
    
    def read_file(self, file, count_newfile, count_oldfile):
        """
        file : Give path of resume file
        docx_parser : Enter docx2txt or tika, by default is tika
        """
        # file = "/content/Asst Manager Trust Administration.docx"
        print("comming to file")
        print("\n\n\n\n File == ",file,"\n\n")
        
        count_newfile = int(count_newfile)
        count_oldfile = int(count_oldfile)
        print(count_newfile, "864")
        file = os.path.join(file)
        print("15")
        if file.endswith('docx'):
            print("in docx")
            resume_lines, raw_text = resumeparse.convert_docx_to_txt(file)
        
        elif file.endswith('doc') or file.endswith('.rtf'):
            print("in doc 781")
            resume_lines, raw_text = resumeparse.convert_doc_to_txt(file)
        
        elif file.endswith('pdf'):
            print("in pdf")
            resume_lines, raw_text = resumeparse.convert_pdf_to_txt(file)
        elif file.endswith('txt'):
            print("in txt")
            with open(file, 'r', encoding='latin') as f:
                resume_lines = f.readlines()

        else:
            resume_lines = None
        resume_segments = resumeparse.segment(resume_lines)
        print("2")
        
        full_text = " ".join(resume_lines)

        email = resumeparse.extract_email(full_text)
        print(email, "882")
        phone = resumeparse.find_phone(full_text)
        
        
        def save_file(file_path, destination_directory, new_filename):
    
            if os.path.isfile(file_path):
        
                destination_path = os.path.join(destination_directory, new_filename)

        
                shutil.copy(file_path, destination_path)

                print(f"File saved successfully at: {destination_path}")
            else:
                print(f"Error: File not found at {file_path}")

        def save_file1(file_path, destination_directory, new_filename):
    
            if os.path.isfile(file_path):
        
                destination_path = os.path.join(destination_directory, new_filename)
                shutil.copy(file_path, destination_path)

                print(f"File saved successfully at: {destination_path}")
            else:
                print(f"Error: File not found at {file_path}")

        

        host = 'localhost'
        user = 'root'
        password = 'raje123456@'
        database = 'multi_threading'

        connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
        )

        cursor = connection.cursor()

        print(email)
        print(phone)

        
        query = "SELECT Email FROM email WHERE Email = %s"
        cursor.execute(query, (email,))

        row = cursor.fetchone()

        if row:
            
            print(f"Row with ID {email} exists:")
            print(row)
            count_newfile +=1
            file_path = file
            destination_directory = "./Old files"
            new_filename = file
            save_file(file_path, destination_directory, new_filename)
            
        else:
            
            print(f"Row with ID {email} does not exist.")
            count_oldfile += 1
            file_path = file
            destination_directory = "./New File"
            new_filename = file
            save_file(file_path, destination_directory, new_filename)
            
        
        
         
        return {
            "email": email,
            "phone": phone,
            "row_newfile": count_newfile,
            "row_oldfile": count_oldfile
            
        }
    
    def display(self):
        print("\n\n ========= Inside display() ========== \n\n")
        
        
parser_obj = resumeparse()
# parsed_resume_data = parser_obj.read_file('sample/Naukri_AbhijeetDey[8y_0m].doc')
# print("\n\n ========== parsed_data ========= \n\n")
