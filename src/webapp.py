import streamlit as st
import requests

import textparser

PARSE_ENDPOINT = "http://localhost:8000/update_database"
SCORE_ENDPOINT = "http://localhost:8000/score_latest"


def parse_and_update_resume(resume_text):
    parsed_info = textparser.get_resume_parse_data(resume_text)
    # Upload the parsed data to FastAPI for updating the resume collection
    response = requests.post(PARSE_ENDPOINT, json=parsed_info, params={"data_type": "resumes"})
    st.text(response.text)


def parse_and_update_job_description(jd_text):
    parsed_info = textparser.get_jd_parse_data(jd_text)
    # Upload the parsed data to FastAPI for updating the job description collection
    response = requests.post(PARSE_ENDPOINT, json=parsed_info, params={"data_type": "job_descriptions",
                                                                       "jd_text": jd_text})
    st.text(response.text)


def auto_score_and_display(data_type):
    response = requests.post(SCORE_ENDPOINT, params={"data_type": data_type})
    if response.status_code == 200:
        top_matches = response.json()["top_matches"]
        st.write(f"Top {data_type} matches:")
        for match in top_matches:
            st.subheader(f"ID: {match['id']}, Score: {match['score']}")
            for key, value in match["parsed_data"].items():
                st.text(f"{key.capitalize()}: {value}")
            st.write("----------------------------------------")
    else:
        st.error("Error in scoring.")


def main():
    st.title("Resume and Job Description Parser")

    # Upload Resume
    st.header("Upload Resume:")
    resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    if resume_file:
        st.success("Resume uploaded successfully!")
        resume_text = textparser.extract_pdf_data(resume_file)
        parse_and_update_resume(resume_text)

    # Upload Job Description
    st.header("Upload Job Description:")
    jd_text = st.text_area("Paste Job Description Text", key="jd_text")
    if jd_text:
        parse_and_update_job_description(jd_text)


    # Button to trigger scoring
    if st.button("Get matches"):
        if jd_text:
            auto_score_and_display(data_type="job_descriptions")
        elif resume_file:
            auto_score_and_display(data_type="resumes")
        else:
            st.warning("Please upload a resume pdf or paste a job description text.")

    st.sidebar.info(
        "Instructions: Upload your resume in PDF format or paste a job description to find the best matching resumes.")


if __name__ == "__main__":
    main()
