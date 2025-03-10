# Registration Name Matcher

## Summary

The Registration Name Matcher is a web application that allows users to upload an Excel file containing registration data and check for similar names using fuzzy matching. The application normalizes the text and compares it against a list of names provided by the user. The results are displayed in a table and can be downloaded as an Excel file.

## Technologies Used

### Frontend

- **Next.js**: A React framework for building server-side rendered and static web applications.
- **TypeScript**: A typed superset of JavaScript that compiles to plain JavaScript.
- **Axios**: A promise-based HTTP client for making API requests.
- **XLSX**: A library for reading and writing Excel files.

### Backend

- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.6+.
- **Uvicorn**: A lightning-fast ASGI server implementation, using `uvloop` and `httptools`.
- **Pandas**: A data analysis and manipulation library for Python.
- **FuzzyWuzzy**: A library for fuzzy string matching.
- **Python-Levenshtein**: A library for fast computation of Levenshtein distance and string similarity.

## Running the Application with Docker

### Prerequisites

- Docker
- Docker Compose

