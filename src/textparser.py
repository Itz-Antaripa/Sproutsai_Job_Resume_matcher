import json
import fitz
from unidecode import unidecode

from reusable_functions import get_answer_from_openai


def extract_pdf_data(file_stream):
    doc = fitz.open(stream=file_stream.read(), filetype="pdf")
    text_blocks = [page.get_text("blocks") for page in doc]
    full_text = "".join(unidecode(block[4]) for page_blocks in text_blocks for block in page_blocks if block[6] == 0)
    doc.close()
    return full_text


def prompt_flow_jd_parser(job_description):
    conversation = []

    system_message = '''You are an expert recruitment assistant specialized in parsing.
Given a job description, you have to extract the necessary information understanding the context and domain.
Necessary information includes keys "job_title", "skills_required", "experience_required", "minimum_education", "job_location", "job_type", "industry/domain"

The return type of response must be in json format like:
{
    "job_title": "Machine Learning Engineer",
    "skills_required": ["Python", "Pytorch", "Numpy", "c++", "GCP"],
    "experience_required": 3 (float datatype),
    "minimum_education": "Bachelors",
    "job_location": "Hyderabad",
    "job_type": "hybrid",
    "domain": "domain on which the company is hiring for"
}

Note:
For experience required take the minimum requirement. If 4-6 years mentioned, take 4.
If some data is not found in job description keep that empty string "".
domain means the domain for which the company is hiring like UI/UX, data science, software engineering, web development, backend engineering, etc.
Job type can be "in-office/hybrid/remote", if nothing mentioned and only location mentioned then job type will be "in-office"
'''

    conversation.append({"role": "system", "content": system_message})
    conversation.append({"role": "user", "content": f'''Job_description: {job_description}.

You are expert job description parser, returning the necessary keys "job_title", "skills_required", "experience_required", "minimum_education", "job_location", "job_type", "industry/domain".
Return only in json format.'''})

    return conversation


def prompt_flow_resume_parser(resume):
    conversation = []

    system_message = '''You are an expert recruitment assistant specialized in resume parsing.
Given a resume data, you have to extract the necessary information understanding the context and domain.
Necessary information includes keys "job_title", "skills", "total_work_experience", "education", "location", "industry/domain"

The return type of response must be in json format like:
{
    "job_title": "Full-stack developer",
    "skills": ["JavaScript", "HTML", "CSS", "Node.js", "Express.js", "Python", "Flask", "Django", "MySQL", "MongoDB", "AWS"],,
    "total_work_experience": 3.8
    "education": "Masters",
    "location": "Bengaluru, India",
    "domain": ["domain on which the person has worked in company 1". "domain in company 2"]
}

Note:
If some data is not found in resume keep that empty string "".
For education only take the latest degree.
For job_title extract the latest one from work experience, for someone with no experience give a desired job_title based on projects done, and other context in resume.
For location take the latest/relevant job location from work experience like -> state, country. If there's no work experience then take location details from last education.
Skills need to be extracted from both the skills section and if anything is mentioned in work experience projects.
Total work experience needs to be calculated from the work experience section, sum of all work experiences considering the gap years if any. Only consider full-time experience not the intern experience.
domain is like in which domain the person has worked like UI/UX, data science, software engineering, web development, backend engineering, etc.
'''

    conversation.append({"role": "system", "content": system_message})
    conversation.append({"role": "user", "content": f'''Resume: {resume}.

You are expert resume parser, returning the necessary keys "job_title", "skills", "work_experience", "total_work_experience", "education", "location", "industry/domain".
Make sure the total work experience is correctly calculated.
Return only in json format.'''})

    return conversation


def get_jd_parse_data(jd_description):
    conversation_prompt = prompt_flow_jd_parser(jd_description)
    response = get_answer_from_openai(conversation_prompt)
    try:
        jd_parser_response = json.loads(response)
    except Exception as e:
        jd_parser_response = {}
    return jd_parser_response


def get_resume_parse_data(resume):
    conversation_prompt = prompt_flow_resume_parser(resume)
    response = get_answer_from_openai(conversation_prompt)
    try:
        resume_parser_response = json.loads(response)
    except Exception as e:
        resume_parser_response = {}
    return resume_parser_response

