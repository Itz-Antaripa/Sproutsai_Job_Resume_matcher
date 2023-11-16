import pandas as pd
import os

import textparser


def update_resume_database_csv_pandas(file, parsed_data, db_path='resume_database.csv'):
    flattened_data = {
        'job_title': parsed_data.get('job_title', ''),
        'skills': ', '.join(parsed_data.get('skills', [])),  # Convert list to string
        'total_work_experience': parsed_data.get('total_work_experience', ''),
        'education': parsed_data.get('education', ''),
        'location': parsed_data.get('location', ''),
        'industry_domain': ', '.join(parsed_data.get('industry/domain', []))  # Convert list to string
    }
    if os.path.isfile(db_path):
        df = pd.read_csv(db_path)
    else:
        df = pd.DataFrame(columns=['id', 'file_name'] + list(flattened_data.keys()))
    # new ID
    new_id = df['id'].max() + 1 if not df.empty else 1
    new_record = pd.DataFrame([{
        'id': new_id,
        'file_name': file,
        **flattened_data
    }])
    # Append new record and save
    df = df.append(new_record, ignore_index=True)
    df.to_csv(db_path, index=False)


def update_job_description_database(description, parsed_data, db_path='job_description_database.csv'):
    flattened_data = {
        'job_title': parsed_data.get('job_title', ''),
        'skills_required': ', '.join(parsed_data.get('skills_required', [])),  # Convert list to string
        'experience_required': parsed_data.get('experience_required', ''),
        'minimum_education': parsed_data.get('minimum_education', ''),
        'job_location': parsed_data.get('job_location', ''),
        'job_type': parsed_data.get('job_type', ''),
        'industry_domain': parsed_data.get('industry/domain', '')
    }
    if os.path.isfile(db_path):
        df = pd.read_csv(db_path)
    else:
        df = pd.DataFrame(columns=['id', 'job_description_text'] + list(flattened_data.keys()))

    # Compute new ID
    new_id = df['id'].max() + 1 if not df.empty else 1

    # Create a new record
    new_record = pd.DataFrame([{
        'id': new_id,
        'job_description_text': description,
        **flattened_data
    }])

    # Append new record and save
    df = df.append(new_record, ignore_index=True)
    df.to_csv(db_path, index=False)


def handle_resume_upload(file_path, resume_data):
    parsed_info = textparser.get_resume_parse_data(resume_data)  # Assuming parser returns JSON
    # update_resume_database_csv_pandas(file_path, parsed_info)
    return parsed_info


def handle_job_description(description):
    parsed_data = textparser.get_jd_parse_data(description)  # Assuming parser returns JSON
    update_job_description_database(description, parsed_data)
    return parsed_data



