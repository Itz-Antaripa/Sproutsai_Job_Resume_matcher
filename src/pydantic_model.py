from typing import List, Optional

from pydantic import BaseModel


class JDParsedData(BaseModel):
    jd_id: int
    job_title: str
    skills_required: List[str]
    experience_required: float
    minimum_education: str
    job_location: str
    job_type: str
    domain: str
    jd_text: Optional[str] = ""


class ResumeParsedData(BaseModel):
    resume_id: int
    job_title: str
    skills: List[str]
    total_work_experience: float
    education: str
    job_location: str
    job_type: str
    domain: List[str]