import json
import os
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv


load_dotenv()  # load .env file

groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize the LLM with Llama 3 70B
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
)

# JSON Schema extraction prompt
parser_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an expert HR data extraction AI. Extract structural information from the provided resume text. "
        "Respond ONLY with a valid JSON object matching this exact schema:\n"
        "{{\n"
        '  "candidate_name": "Full Name or Unknown",\n'
        '  "education_level": "Intermediate" or "Bachelor\'s" or "Master\'s" or "PhD",\n'
        '  "experience_years": integer,\n'
        '  "universities": ["University 1", "University 2"],\n'
        '  "fit_score": integer (between 1 and 100 assessing alignment with the Job Description),\n'
        '  "justification": "Short 2-sentence summary of why this score was given."\n'
        "}}\n"
        "Ensure data types match. If education level is ambiguous, default to the closest lower match. "
        "Base your fit_score strictly on the provided Job Description."
    )),
    ("human", "Job Description:\n{job_description}\n\nResume Text:\n{resume_text}")
])

def map_education_level(level: str) -> int:
    levels = {"Intermediate": 1, "Bachelor's": 2, "Master's": 3, "PhD": 4}
    return levels.get(level, 0)

def analyze_resumes(resumes: List[Dict[str, Any]], job_description: str, filters: Dict[str, Any], scale: int) -> List[Dict[str, Any]]:
    processed_candidates = []
    chain = parser_prompt | llm | JsonOutputParser()

    for res in resumes:
        try:
            # AI Extraction and Scoring
            ai_response = chain.invoke({
                "job_description": job_description,
                "resume_text": res["text"]
            })
            
            candidate = {
                "filename": res["filename"],
                "name": ai_response.get("candidate_name", "Unknown"),
                "education": ai_response.get("education_level", "Bachelor's"),
                "experience": int(ai_response.get("experience_years", 0)),
                "universities": ai_response.get("universities", []),
                "score": int(ai_response.get("fit_score", 0)),
                "justification": ai_response.get("justification", "")
            }
            processed_candidates.append(candidate)
        except Exception as e:
            print(f"Error parsing {res['filename']}: {e}")
            # Fallback structure if LLM fails for one resume
            processed_candidates.append({
                "filename": res["filename"], "name": "Error Parsing", "education": "Intermediate",
                "experience": 0, "universities": [], "score": 0, "justification": "Failed to parse resume."
            })

    # --- APPLY FILTERS ---
    filtered_candidates = []
    min_edu_rank = map_education_level(filters.get("education"))
    min_exp = filters.get("min_exp")
    max_exp = filters.get("max_exp")
    target_unis = [u.strip().lower() for u in filters.get("universities", []) if u.strip()]

    for c in processed_candidates:
        # 1. Education Filter
        if min_edu_rank > 0 and map_education_level(c["education"]) < min_edu_rank:
            continue
        # 2. Experience Filter
        if min_exp is not None and c["experience"] < min_exp:
            continue
        if max_exp is not None and c["experience"] > max_exp:
            continue
        # 3. University Filter (Match if any candidate university matches any target university)
        if target_unis:
            cand_unis = [u.lower() for u in c["universities"]]
            if not any(any(t_uni in cand_u for t_uni in target_unis) for cand_u in cand_unis):
                continue
                
        filtered_candidates.append(c)

    # --- APPLY SHORTLIST SCALE ---
    # Sort candidates dynamically by score (descending)
    filtered_candidates.sort(key=lambda x: x["score"], reverse=True)
    
    total_uploaded = len(resumes)
    shortlist_count = max(1, round((scale / 100) * total_uploaded))
    
    return filtered_candidates[:shortlist_count]