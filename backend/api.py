import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
from fuzzywuzzy import fuzz
import io

app = FastAPI()

# Get CORS origins from environment variable or use default
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mapping for common number-to-letter substitutions
substitution_map = {
    '4': 'A',  # 4 can be A
    '5': 'S',  # 5 can be S
    '1': 'I',  # 1 can be I
    '0': 'O',  # 0 can be O
    '3': 'E',  # 3 can be E
    '2': 'Z',  # 2 can be Z
    '6': 'G',  # 6 can be G
    '7': 'T',  # 7 can be T
    '8': 'B',  # 8 can be B
    '9': 'P',  # 9 can be P
}

def normalize_text(text):
    """
    Normalize text by:
      - Converting to string, stripping leading/trailing whitespace,
      - Converting to uppercase,
      - Removing all spaces,
      - Replacing any numbers with their letter equivalents.
    """
    # Convert to string, remove leading/trailing spaces, convert to uppercase
    text = str(text).strip().upper()
    # Remove all spaces
    text = text.replace(" ", "")
    # Replace numbers with letters based on the substitution map
    normalized = []
    for char in text:
        normalized.append(substitution_map.get(char, char))
    return ''.join(normalized)

def check_for_similar_names(names, registrations):
    """
    Check if any registration plate (normalized) is a close fuzzy match
    to any of the given names (also normalized), using fuzzy matching.
    Returns a list of dictionaries: {lot_number, name, registration, normalized_registration, similarity}.
    """
    all_comparisons = []
    # Normalize target names
    normalized_names = {name: normalize_text(name) for name in names}
    for lot_number, registration in registrations:
        normalized_registration = normalize_text(registration)
        for name, normalized_name in normalized_names.items():
            # Use fuzzy partial ratio to allow extra characters around the match
            similarity = fuzz.partial_ratio(normalized_name, normalized_registration)
            # Store all comparisons
            all_comparisons.append({
                "lot_number": lot_number,
                "name": name,
                "registration": registration,
                "normalized_registration": normalized_registration,
                "similarity": similarity
            })
    return all_comparisons

@app.post("/uploadfile/")
async def create_upload_file(
    file: UploadFile = File(...),
    names: str = Form(default="")
):
    try:
        # Read the uploaded file
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents), header=None, skiprows=5)

        # Extract lot numbers and registrations
        registrations = list(zip(df.iloc[:, 0].dropna(), df.iloc[:, 1].dropna()))

        # Convert names to list (if empty string, use empty list)
        names_to_check = names.split(',') if names else []

        # Get similar registrations using fuzzy matching
        all_comparisons = check_for_similar_names(names_to_check, registrations)

        return JSONResponse(content={"comparisons": all_comparisons})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}