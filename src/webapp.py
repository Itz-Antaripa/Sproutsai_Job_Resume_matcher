import streamlit as st

from textparser import extract_pdf_data
from update_database import handle_resume_upload, handle_job_description

# Streamlit UI Layout
st.title("Resume Matcher")

# Using columns for a cleaner layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload your resume")
    resume_file = st.file_uploader("", type=['pdf'])
    if resume_file:
        st.success("Resume uploaded successfully!")
        resume_text = extract_pdf_data(resume_file)
        parsed_data = handle_resume_upload("some_path.pdf", resume_text)
        if parsed_data:
            st.json(parsed_data)

with col2:
    st.subheader("Enter Job Description")
    job_desc = st.text_area("", height=250)

# Action button
if st.button('Match'):
    if job_desc:
        top_resumes = handle_job_description(job_desc)
        # Display top resumes
        st.write("Top Resume Matches:")
        for resume in top_resumes:
            st.write(resume)
    else:
        st.error("Please upload a resume or enter a job description.")

# Additional instructions or information
st.sidebar.info("Instructions: Upload your resume in PDF format or paste a job description to find the best matching resumes.")

