from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from pymongo import MongoClient
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Optional

from matching_algorithm import Scorer
from pydantic_model import ResumeParsedData, JDParsedData

app = FastAPI()

# Connect to MongoDB (ensure MongoDB is running on localhost:27017)
client = MongoClient("mongodb://localhost:27017/")
db = client["mongob-db-sproutsai"]


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application!"}


@app.post("/update_database")
async def update_database(parsed_data: dict,
                          jd_text: Optional[str] = Query("", description="JD Text"),
                          data_type: str = Query(..., description="Type of Parsed Data (resume or job_description)")):
    collection_name = data_type.lower()
    id = db[collection_name].count_documents({}) + 1
    if collection_name == "resumes":
        parsed_data["resume_id"] = id
        parsed_data = ResumeParsedData(**parsed_data)
    else:
        parsed_data["jd_id"] = id
        parsed_data = JDParsedData(**parsed_data, jd_text=jd_text)  # Initialize jd_text as empty string
    # Update MongoDB collection with parsed data
    db[collection_name].insert_one(jsonable_encoder(parsed_data))

    return JSONResponse(content={"message": f"{collection_name} parsed and updated successfully"})


@app.post("/score_latest")
async def score_latest(data_type: str = Query(..., description="Type of Data (resume or job_description)")):
    collection_name = data_type.lower()

    if collection_name == "resumes":
        latest_resume = db.resumes.find().sort([("_id", -1)]).limit(1)[0]
        job_descriptions = list(db.job_descriptions.find())
        scores = []
        for jd in job_descriptions:
            scorer = Scorer(resume=latest_resume, job=jd)
            score = scorer.calculate_final_score()
            scores.append({
                "id": jd["jd_id"],
                "score": score,
                "parsed_data": {
                    "job_title": jd["job_title"],
                    "skills_required": jd["skills_required"],
                    "experience_required": jd["experience_required"],
                    "job_location": jd["job_location"],
                    "domain": jd["domain"]
                }
            })

        top_scores = sorted(scores, key=lambda x: x['score'], reverse=True)[:5]
    else:
        latest_job_desc = db.job_descriptions.find().sort([("_id", -1)]).limit(1)[0]
        resumes = list(db.resumes.find())
        scores = []
        for resume in resumes:
            scorer = Scorer(resume=resume, job=latest_job_desc)
            score = scorer.calculate_final_score()
            scores.append({
                "id": resume["resume_id"],
                "score": score,
                "parsed_data": {
                    "job_title": resume["job_title"],
                    "skills": resume["skills"],
                    "total_work_experience": resume["total_work_experience"],
                    "domain": resume["domain"]
                }
            })
        top_scores = sorted(scores, key=lambda x: x['score'], reverse=True)[:5]

    return JSONResponse(content={"top_matches": top_scores})


if __name__ == "__main__":
    import uvicorn
    # Run FastAPI with uvicorn
    uvicorn.run(app)
