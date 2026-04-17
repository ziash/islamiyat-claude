#!/bin/bash
# Launch the IGCSE Islamiyat Exam Prep System
cd "$(dirname "$0")"
source venv/bin/activate
cd islamiyat_prep
echo "Starting IGCSE Islamiyat Exam Prep System..."
echo "Open http://localhost:8501 in your browser"
streamlit run app.py --server.port 8501
