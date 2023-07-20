import openai
import string
import os
from dotenv import load_dotenv
import ast
from unicodedata import normalize
import json
import docx
from ast import literal_eval
import pandas as pd
from pypdf import PdfReader
import pyodbc

class readFile:
    def __init__(self, filepath):
        self.filepath = filepath
    
    def read_file(self):
        file_extension = self.filepath.split('.')[-1].lower()

        if file_extension == 'pdf':
            return self.read_pdf()
        elif file_extension == 'docx':
            return self.read_docx()
        else:
            print("Unsupported file type.")
    
    def read_pdf(self):
        reader = PdfReader(self.filepath)
        number_of_pages = len(reader.pages)
        page = reader.pages[0]
        text = page.extract_text()
        return text
    
    def read_docx(self):
        doc = docx.Document(self.filepath)
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        text = '\n'.join(fullText)
        return text


class summary:

    def __init__(self, resume):
        self.resume = resume

    
    def test(self):
    
        prompt = f"""Summarize the text below into a JSON format with exactly the following structure 
        {{
        basic_info: {{id, first_name, last_name, full_name, email, phone_number, location, portfolio_website_url, linkedin_url, github_main_page_url}}, 
        skills:[skill1, skill2, skill3],
        work_experience: [{{job_title, company, location, duration, job_summary}}], 
        project_experience:[{{project_name, project_description}}],
        education:[{{institution_name, degree_or_stream, year_of_completion, location, GPA}}],
        positions_of_responsibility:[{{designation, organisation_name, duration, summary}}],
        interests:[interest1,interest2,interest3]
        achievements:[]
        }}
        Also, develop a unique key for every different text.Don't use "abcde" as a key. The key should be always different and should be containing minimum 5 characters which will be different every time when a new resume is given and insert that key in the "id" slot as text. Make a different key at every time as it works as an id fopr every employee.For every employee id would be different, so make sure id is always different. You acn also dvelop the id using text that will given.      
        If no value is provided for any of the above keys, put NAN in front of that key.
        {self.resume.replace('"', r'/"')}"""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}], 
            temperature=0.0,
        )
        score = response.choices[0]["message"]["content"]

        return score.replace('"',"'")


    
    def dataframe(self):
        output = self.test()
        result_json = literal_eval(output)
        df_bd = pd.DataFrame(columns = ['id', 'first_name', 'last_name', 'full_name', 'email', 'phone_number', 'location', 'portfolio_website_url', 'linkedin_url', 'github_main_page_url'])
        df_work_exp = pd.DataFrame(columns = ['id', 'job_title', 'company', 'location', 'duration', 'job_summary'])
        df_project_exp = pd.DataFrame(columns = ['id', 'project_name', 'project_description'])
        df_por = pd.DataFrame(columns = ['id', 'designation', 'organisation_name', 'duration', 'summary'])
        df_edu = pd.DataFrame(columns = ['id', 'institution_name', 'degree', 'year_of_completion', 'location', 'GPA'])
        df_skills = pd.DataFrame(columns = ['id', 'skills'])
        df_interests = pd.DataFrame(columns = ['id', 'interests'])
        df_achievements = pd.DataFrame(columns = ['id', 'achievements'])

        df_bd = df_bd.append({'id': result_json["basic_info"]["id"], 'first_name': result_json["basic_info"]["first_name"], 'last_name': result_json["basic_info"]["last_name"], 'full_name': result_json["basic_info"]["full_name"], 'email': result_json["basic_info"]["email"], 'phone_number': result_json["basic_info"]["phone_number"], 'location': result_json["basic_info"]["location"], 'portfolio_website_url': result_json["basic_info"]["portfolio_website_url"], 'linkedin_url': result_json["basic_info"]["linkedin_url"], 'github_main_page_url': result_json["basic_info"]["github_main_page_url"]}, ignore_index=True)
        
        for i in range(0, len(result_json["work_experience"])):
            df_work_exp = df_work_exp.append({'id': result_json["basic_info"]["id"], 'job_title': result_json["work_experience"][i]["job_title"], 'company': result_json["work_experience"][i]["company"], 'location': result_json["work_experience"][i]["location"], 'duration': result_json["work_experience"][i]["duration"], 'job_summary': result_json["work_experience"][i]["job_summary"]}, ignore_index=True)
        
        for i in range(0, len(result_json["project_experience"])):
            df_project_exp = df_project_exp.append({'id': result_json["basic_info"]["id"], 'project_name': result_json["project_experience"][i]["project_name"], 'project_description': result_json["project_experience"][i]["project_description"]}, ignore_index=True)
        
        for i in range(0, len(result_json["positions_of_responsibility"])):
            df_por = df_por.append({'id': result_json["basic_info"]["id"], 'designation': result_json["positions_of_responsibility"][i]["designation"], 'organisation_name': result_json["positions_of_responsibility"][i]["organisation_name"], 'duration': result_json["positions_of_responsibility"][i]["duration"], 'summary': result_json["positions_of_responsibility"][i]["summary"]}, ignore_index=True)
        
        for i in range(0, len(result_json["education"])):
            df_edu = df_edu.append({'id': result_json["basic_info"]["id"], 'institution_name': result_json["education"][i]["institution_name"], 'degree': result_json["education"][i]["degree_or_stream"], 'year_of_completion': result_json["education"][i]["year_of_completion"], 'location': result_json["education"][i]["location"], 'GPA': result_json["education"][i]["GPA"]}, ignore_index=True)

        for i in range(0, len(result_json["skills"])):
            df_skills = df_skills.append({'id': result_json["basic_info"]["id"], 'skills': result_json["skills"][i]}, ignore_index=True)

        for i in range(0, len(result_json["interests"])):
            df_interests = df_interests.append({'id': result_json["basic_info"]["id"], 'interests': result_json["interests"][i]}, ignore_index=True)
        
        for i in range(0, len(result_json["achievements"])):
            df_achievements = df_achievements.append({'id': result_json["basic_info"]["id"], 'achievements': result_json["achievements"][i]}, ignore_index=True)

        return df_bd, df_work_exp, df_project_exp, df_por, df_edu, df_skills, df_interests, df_achievements
    


def create_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS basic_details")
    cursor.execute("DROP TABLE IF EXISTS work_experience")
    cursor.execute("DROP TABLE IF EXISTS project_experience")
    cursor.execute("DROP TABLE IF EXISTS por")
    cursor.execute("DROP TABLE IF EXISTS education")
    cursor.execute("DROP TABLE IF EXISTS skills")
    cursor.execute("DROP TABLE IF EXISTS interests")
    cursor.execute("DROP TABLE IF EXISTS achievements")

    cursor.execute("CREATE TABLE basic_details (id VARCHAR(300), first_name VARCHAR(300), last_name VARCHAR(300), full_name VARCHAR(300), email VARCHAR(300), phone_number VARCHAR(300), location VARCHAR(300), portfolio_website_url VARCHAR(300), linkedin_url VARCHAR(300), github_main_page_url VARCHAR(300))")
    cursor.execute("CREATE TABLE work_experience (id VARCHAR(300), job_title VARCHAR(300), company VARCHAR(300), location VARCHAR(300), duration VARCHAR(300), job_summary VARCHAR(1000))")
    cursor.execute("CREATE TABLE project_experience (id VARCHAR(300), project_name VARCHAR(300), project_description VARCHAR(1000))")
    cursor.execute("CREATE TABLE por (id VARCHAR(300), designation VARCHAR(300), organisation_name VARCHAR(300), duration VARCHAR(300), summary VARCHAR(300))")
    cursor.execute("CREATE TABLE education (id VARCHAR(300), institution_name VARCHAR(300), degree VARCHAR(300), year_of_completion VARCHAR(300), location VARCHAR(300), GPA VARCHAR(300))")
    cursor.execute("CREATE TABLE skills (id VARCHAR(300), skills VARCHAR(1000))")
    cursor.execute("CREATE TABLE interests (id VARCHAR(300), interests VARCHAR(300))")
    cursor.execute("CREATE TABLE achievements (id VARCHAR(300), achievements VARCHAR(600))")

    conn.commit()


def insert_values(cursor, df_bd, df_work_exp, df_project_exp, df_por, df_edu, df_skills, df_interests, df_achievements):    
    for index,row in df_bd.iterrows():
        cursor.execute("INSERT INTO dbo.basic_details([id], [first_name], [last_name], [full_name], [email], [phone_number], [location], [portfolio_website_url], [linkedin_url], [github_main_page_url]) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", str(row.id), str(row.first_name), str(row.last_name), str(row.full_name), str(row.email), str(row.phone_number), str(row.location), str(row.portfolio_website_url), str(row.linkedin_url), str(row.github_main_page_url))

    for index,row in df_work_exp.iterrows():
        cursor.execute("INSERT INTO dbo.work_experience([id], [job_title], [company], [location], [duration], [job_summary]) values(?, ?, ?, ?, ?, ?)", str(row.id), str(row.job_title), str(row.company), str(row.location), str(row.duration), str(row.job_summary))

    for index,row in df_project_exp.iterrows():
        cursor.execute("INSERT INTO dbo.project_experience([id], [project_name], [project_description]) values(?, ?, ?)", str(row.id), str(row.project_name), str(row.project_description))

    for index,row in df_por.iterrows():
        cursor.execute("INSERT INTO dbo.por([id], [designation], [organisation_name], [duration], [summary]) values(?, ?, ?, ?, ?)", str(row.id), str(row.designation), str(row.organisation_name), str(row.duration), str(row.summary))

    for index,row in df_edu.iterrows():
        cursor.execute("INSERT INTO dbo.education([id], [institution_name], [degree], [year_of_completion], [location], [GPA]) values(?, ?, ?, ?, ?, ?)", str(row.id), str(row.institution_name), str(row.degree), str(row.year_of_completion), str(row.location), str(row.GPA))
    
    for index,row in df_skills.iterrows():
        cursor.execute("INSERT INTO dbo.skills([id], [skills]) values(?, ?)", str(row.id), str(row.skills))

    for index,row in df_interests.iterrows():
        cursor.execute("INSERT INTO dbo.interests([id], [interests]) values(?, ?)", str(row.id), str(row.interests)) 

    for index,row in df_achievements.iterrows():
        cursor.execute("INSERT INTO dbo.achievements([id], [achievements]) values(?, ?)", str(row.id), str(row.achievements))
    conn.commit()


def insert_to_db(filename):
    resume = readFile(filename).read_file()
    df_bd, df_work_exp, df_project_exp, df_por, df_edu, df_skills, df_interests, df_achievements = summary(resume).dataframe()
    insert_values(cursor, df_bd, df_work_exp, df_project_exp, df_por, df_edu, df_skills, df_interests, df_achievements)




load_dotenv()

openai.api_key = ""
chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}])

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=;'
                      'Database=;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

print("creating new table.....")
create_table(cursor)



# print("creating table.....")
# create_table(cursor)
# conn.commit()

# insert_to_db('test1.pdf')
