from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["mongob-db-sproutsai"]

# Create collections
db.create_collection("resumes")
db.create_collection("job_descriptions")
