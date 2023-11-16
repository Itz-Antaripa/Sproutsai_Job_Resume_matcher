from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from reusable_functions import get_embedding


class Scoring:

    def __init__(self, resumes, jobs):
        self.resumes = resumes
        self.jobs = jobs
        self.model = SentenceTransformer('all-mpnet-base-v2')

        # Define degree mapping and importance levels
        self.degree_mapping = {
            "bachelor": ["bachelor", "b.tech", "b.e.", "b.eng", "b.sc"],
            "master": ["master", "m.eng", "m.sc", "m.e.", "m.s."],
            "phd": ["phd", "doctorate", "doctor of philosophy", "d.phil"]
        }
        self.degree_levels = {"bachelor": 1, "master": 2, "phd": 3}

    # degree matching
    def map_degree_to_level(self, degree):
        for level, degree_list in self.degree_mapping.items():
            if any(d.lower() in degree.lower() for d in degree_list):
                return level
        return None

    def degree_matching(self, resume, job):
        resume_level = self.map_degree_to_level(resume["education"])
        job_level = self.map_degree_to_level(job["minimum_education"])

        if resume_level and job_level:
            level_difference = abs(self.degree_levels[resume_level] - self.degree_levels[job_level])
            return max(0, 1 - 0.2 * level_difference)
        elif job_level is None and resume_level:
            return 0.5  # If education is not mentioned in the job description
        else:
            return 0.2  # Assign a default score if mapping is not available

    # title and domain matching
    def title_domain_matching(self, resume, job):
        # Fuzzy matching for title and domain
        title_match = fuzz.partial_ratio(resume["job_title"].lower(), job["job_title"].lower())
        domain_match = max(
            fuzz.partial_ratio(domain.lower(), job["industry/domain"].lower()) for domain in resume["domain"])
        # Embeddings matching
        resume_title_embedding = get_embedding(resume["job_title"] + "," + ",".join(resume["domain"]))
        job_title_embedding = get_embedding(job["job_title"] + "," + job["domain"])
        domain_similarity = cosine_similarity(resume_title_embedding, job_title_embedding)
        # Combine keyword matching and embeddings similarity
        score = max(title_match, domain_match, domain_similarity)
        return round(score, 2)

    def skills_matching(self, resume, job):
        # Fuzzy matching for skills
        max_skill_similarity = max(
            fuzz.partial_ratio(skill.lower(), job_skill.lower()) for skill in resume["skills"] for job_skill in
            job["skills_required"])
        # Embeddings matching
        resume_skills_embedding = get_embedding(" ".join(resume["skills"]))
        job_skills_embedding = get_embedding(" ".join(job["skills_required"]))
        skills_similarity = cosine_similarity(resume_skills_embedding, job_skills_embedding)
        # Combine fuzzy matching and embeddings similarity
        combined_score = (max_skill_similarity + skills_similarity) / 2
        return round(combined_score, 2)

    def experience_matching(self, resume, job):
        candidate_experience = resume["total_work_experience"]
        required_experience = job["experience_required"]
        exp_diff = abs(candidate_experience - required_experience)
        exp_diff = min(5, exp_diff)  # here above 5 as max diff we will consider the difference as 5
        score = 1 - (0.1 * exp_diff)
        return round(score, 2)

    def location_matching(self, resume, job):
        if job.get("job_type", "").lower() == "remote":
            return 1.0  # Full score for remote jobs
        # Check if a location is mentioned in the job description
        job_location = job.get("job_location", "")
        if not job_location:
            return 1.0
        # Check if the job's location matches the candidate's location
        candidate_location = resume.get("location", "")
        if candidate_location.lower() in job_location.lower():
            return 1.0
        elif candidate_location.lower().split()[-1] == job_location.lower().split()[-1]:
            return 0.8  # Partial score for matching countries
        else:
            return 0.0

