from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from reusable_functions import get_embedding


class Scorer:

    def __init__(self, resume, job):
        self.resume = resume
        self.job = job

        # Define degree mapping and importance levels
        self.degree_mapping = {
            "bachelor": ["bachelor", "b.tech", "b.e", "b.eng", "b.sc", "bsc", "undergraduate"],
            "master": ["master", "m.eng", "m.sc", "m.e.", "m.s", "ms", "graduate"],
            "phd": ["phd", "ph.d", "doctorate", "research"]
        }
        self.degree_levels = {"bachelor": 1, "master": 2, "phd": 3}

    # degree matching
    def map_degree_to_level(self, degree):
        for level, degree_list in self.degree_mapping.items():
            if any(d.lower() in degree.lower() for d in degree_list):
                return level
        return None

    def degree_matching(self):
        resume_level = self.map_degree_to_level(self.resume["education"])
        job_level = self.map_degree_to_level(self.job["minimum_education"])

        if resume_level and job_level:
            level_difference = abs(self.degree_levels[resume_level] - self.degree_levels[job_level])
            return max(0, 1 - 0.2 * level_difference)
        elif job_level is None and resume_level:
            return 0.5  # If education is not mentioned in the job description
        else:
            return 0.2  # Assigning a default score if mapping is not available

    # title and domain matching
    def title_domain_matching(self):
        # Embeddings matching
        resume_title_embedding = np.array(get_embedding(self.resume["job_title"])).reshape(1, -1)
        resume_domain_embedding = np.array(get_embedding(",".join(self.resume["domain"]))).reshape(1, -1)
        job_title_embedding = np.array(get_embedding(self.job["job_title"])).reshape(1, -1)
        title_similarity = cosine_similarity(resume_title_embedding, job_title_embedding)[0][0]
        domain_similarity = cosine_similarity(resume_domain_embedding, job_title_embedding)[0][0]
        # Combine embeddings similarity
        score = max(title_similarity, domain_similarity)
        return round(score, 2)

    def skills_matching(self):
        # Embeddings matching
        resume_skills_embedding = np.array(get_embedding(" ".join(self.resume["skills"]))).reshape(1, -1)
        job_skills_embedding = np.array(get_embedding(" ".join(self.job["skills_required"]))).reshape(1, -1)
        skills_similarity = cosine_similarity(resume_skills_embedding, job_skills_embedding)[0][0]
        return round(skills_similarity, 2)

    def experience_matching(self):
        candidate_experience = self.resume["total_work_experience"]
        required_experience = self.job["experience_required"]
        exp_diff = abs(candidate_experience - required_experience)
        exp_diff = min(5, exp_diff)  # here above 5 as max diff we will consider the difference as 5
        score = 1 - (0.1 * exp_diff)
        return round(score, 2)

    def location_matching(self):
        if self.job.get("job_type", "").lower() == "remote":
            return 1.0  # Full score for remote jobs
        # Check if a location is mentioned in the job description
        job_location = self.job.get("job_location", "")
        if not job_location:
            return 1.0
        # Check if the job's location matches the candidate's location
        candidate_location = self.resume.get("location", "")
        if candidate_location.lower() in job_location.lower():
            return 1.0
        elif candidate_location.lower().split()[-1] == job_location.lower().split()[-1]:
            return 0.8  # Partial score for matching countries
        else:
            return 0.4

    def calculate_final_score(self):
        # Define weights for each matching component
        weight_degree = 0.1
        weight_title_domain = 0.3
        weight_skills = 0.25
        weight_experience = 0.2
        weight_location = 0.15

        # Calculate individual scores
        score_degree = self.degree_matching()
        score_title_domain = self.title_domain_matching()
        score_skills = self.skills_matching()
        score_experience = self.experience_matching()
        score_location = self.location_matching()
        print(score_degree, score_title_domain, score_skills, score_experience, score_location)

        # Combine scores with weights
        final_score = (
                weight_degree * score_degree +
                weight_title_domain * score_title_domain +
                weight_skills * score_skills +
                weight_experience * score_experience +
                weight_location * score_location
        )

        # Normalize the final score to be between 0 and 100
        final_score_percent = round(final_score * 100, 2)

        return final_score_percent

