import pandas as pd
import re
from fuzzywuzzy import fuzz
import tkinter as tk
from tkinter import filedialog, messagebox
import os

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

def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def add_name():
    name = name_entry.get()
    if name:
        names_listbox.insert(tk.END, name)
        name_entry.delete(0, tk.END)

def run_comparison():
    file_path = file_entry.get()
    if not file_path:
        messagebox.showerror("Error", "Please select a file.")
        return

    names_to_check = names_listbox.get(0, tk.END)
    if not names_to_check:
        messagebox.showerror("Error", "Please add names to check.")
        return

    try:
        df = pd.read_excel(file_path, header=None, skiprows=5)
        registrations = df.iloc[:, 1].dropna().tolist()
        matches, all_comparisons = check_for_similar_names(names_to_check, registrations, threshold=80)

        df_all_comparisons = pd.DataFrame(all_comparisons, columns=['Name', 'Registration', 'Normalized Registration', 'Similarity'])
        df_matches = pd.DataFrame(matches, columns=['Name', 'Registration', 'Normalized Registration', 'Similarity'])

        output_file_path = os.path.abspath('./Registration_Matches.xlsx')
        with pd.ExcelWriter(output_file_path) as writer:
            df_all_comparisons.to_excel(writer, sheet_name='All Comparisons', index=False)
            df_matches.to_excel(writer, sheet_name='Matches', index=False)

        messagebox.showinfo("Success", f"Results have been written to {output_file_path}")
        os.startfile(output_file_path)  # Open the Excel file
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create the main window
root = tk.Tk()
root.title("Registration Name Matcher")

# Create and place the widgets
tk.Label(root, text="Select Excel File:").grid(row=0, column=0, padx=10, pady=10)
file_entry = tk.Entry(root, width=50)
file_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=load_file).grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text="Add Name to Check:").grid(row=1, column=0, padx=10, pady=10)
name_entry = tk.Entry(root, width=50)
name_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="Add", command=add_name).grid(row=1, column=2, padx=10, pady=10)

tk.Label(root, text="Names to Check:").grid(row=2, column=0, padx=10, pady=10)
names_listbox = tk.Listbox(root, width=50, height=10)
names_listbox.grid(row=2, column=1, padx=10, pady=10, columnspan=2)

# Add default names to the listbox
default_names = ["Asim", "Suna", "Sue", "Kay", "Kayhan", "Kai", "Niz"]
for name in default_names:
    names_listbox.insert(tk.END, name)

tk.Button(root, text="Run Comparison", command=run_comparison).grid(row=3, column=0, columnspan=3, padx=10, pady=10)

# Start the main event loop
root.mainloop()