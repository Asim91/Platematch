import pandas as pd
import re
from fuzzywuzzy import fuzz

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

def check_for_similar_names(names, registrations, threshold=80):
    """
    Check if any registration plate (normalized) is a close fuzzy match
    to any of the given names (also normalized), using fuzzy matching.
    Returns a list of tuples: (target name, original registration, normalized registration, similarity score).
    """
    similar_registrations = []
    all_comparisons = []
    # Normalize target names
    normalized_names = {name: normalize_text(name) for name in names}
    for registration in registrations:
        normalized_registration = normalize_text(registration)
        for name, normalized_name in normalized_names.items():
            # Use fuzzy partial ratio to allow extra characters around the match
            similarity = fuzz.partial_ratio(normalized_name, normalized_registration)
            # Store all comparisons
            all_comparisons.append((name, registration, normalized_registration, similarity))
            if similarity >= threshold:
                similar_registrations.append((name, registration, normalized_registration, similarity))
    return similar_registrations, all_comparisons

# ---------------------------
# Load registrations from Excel
# ---------------------------

# Change the file path to point to your Excel file
file_path = './March_2025_DVLA_Timed_Online_Auction_Registrations.xlsx'  # <-- Update this path!

# Read the Excel file; skip the first 5 rows so that data starts at row 6
df = pd.read_excel(file_path, header=None, skiprows=5)

# Data now starts in column B, so we use column index 1 (0-indexed)
registrations = df.iloc[:, 1].dropna().tolist()

# ---------------------------
# Set the names to search for
# ---------------------------
names_to_check = ["Asim", "Suna", "Sue", "Kay", "Kayhan", "Kai", "Niz"]

# Get similar registrations using fuzzy matching
matches, all_comparisons = check_for_similar_names(names_to_check, registrations, threshold=80)

# ---------------------------
# Output the results to Excel
# ---------------------------
# Create DataFrames for the results
df_all_comparisons = pd.DataFrame(all_comparisons, columns=['Name', 'Registration', 'Normalized Registration', 'Similarity'])
df_matches = pd.DataFrame(matches, columns=['Name', 'Registration', 'Normalized Registration', 'Similarity'])

# Write the DataFrames to an Excel file with two sheets
output_file_path = './Registration_Matches.xlsx'
with pd.ExcelWriter(output_file_path) as writer:
    df_all_comparisons.to_excel(writer, sheet_name='All Comparisons', index=False)
    df_matches.to_excel(writer, sheet_name='Matches', index=False)

print(f"Results have been written to {output_file_path}")
