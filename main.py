from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from pinecone import Pinecone
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("courses-data")

app = FastAPI()

class SearchRequest(BaseModel):
    query: str
    answers: dict
    top_k: int = 40

@app.post("/api/search")
async def search_courses(req: SearchRequest):
    print(f"📥 Received query: {req.query}")
    print(f"📥 Answers: {req.answers}")

    # Generate embedding from query
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=req.query
    ).data[0].embedding

    # Build Pinecone filters
    pinecone_filter = {}
    if req.answers.get("country"):
        pinecone_filter["country"] = {"$eq": req.answers["country"]}
    if req.answers.get("discipline"):
        pinecone_filter["discipline"] = {"$eq": req.answers["discipline"]}
    if req.answers.get("degree"):
        pinecone_filter["degree"] = {"$eq": req.answers["degree"]}
    if req.answers.get("study_level"):
        pinecone_filter["study_level"] = {"$eq": req.answers["study_level"]}
    if req.answers.get("duration"):
        pinecone_filter["duration"] = {"$eq": req.answers["duration"]}
    if req.answers.get("budget"):
        try:
            pinecone_filter["course_fee"] = {"$lt": float(req.answers["budget"])}
        except:
            pass

    print(f"📥 Pinecone filter being sent: {pinecone_filter}")

    # Query Pinecone with filters first
    results = index.query(
        vector=embedding,
        top_k=req.top_k,
        filter=pinecone_filter,
        include_metadata=True
    )

    matches = [
        {
            "id": m["id"],
            "score": m["score"],
            **m["metadata"]
        }
        for m in results["matches"]
    ]

    print(f"📤 Raw matches from Pinecone: {len(results['matches'])}")
    print(f"📤 Matches after parsing: {len(matches)}")

    # 🔥 Fallback: if no matches, retry without filters
    if not matches:
        print("⚠️ No matches with filters — retrying without filters...")
        results = index.query(
            vector=embedding,
            top_k=req.top_k,
            include_metadata=True
        )
        matches = [
            {
                "id": m["id"],
                "score": m["score"],
                **m["metadata"]
            }
            for m in results["matches"]
        ]
        print(f"📤 Fallback matches: {len(matches)}")

    return {"matches": matches}
