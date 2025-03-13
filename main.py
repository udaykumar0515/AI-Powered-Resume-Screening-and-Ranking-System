import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import time
import re
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime

# Constants
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

# Function to extract contact information
def extract_contact_info(text):
    email = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    phone = re.findall(r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}", text)
    return {"Email": email, "Phone": phone}

def extract_experience(text):
    # Match variations like "2 years", "5+ yrs", "experience of 3 years"
    match = re.search(r"(\d+\+?)\s*(years?|yrs?)|experience\s+of\s+(\d+)\s*(years?|yrs?)", text, re.IGNORECASE)
    if match:
        # Extract the first or third group and remove any non-numeric characters (like '+')
        years_str = (match.group(1) or match.group(3)).replace("+", "")
        years = int(years_str)  # Convert to integer
        if years < 2:
            return "Entry-level"
        elif 2 <= years <= 5:
            return "Mid-level"
        else:
            return "Senior"
    return "Unknown"

# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text

# Function to check for duplicate resumes
def check_duplicates(resumes):
    vectorizer = TfidfVectorizer().fit_transform(resumes)
    vectors = vectorizer.toarray()
    similarity_matrix = cosine_similarity(vectors)
    duplicates = []
    for i in range(len(similarity_matrix)):
        for j in range(i + 1, len(similarity_matrix)):
            if similarity_matrix[i][j] > 0.9:  # Threshold for duplicates
                duplicates.append((uploaded_files[i].name, uploaded_files[j].name))
    return duplicates

# Function to classify rank labels
def get_rank_label(score):
    if score >= 80:
        return "Excellent ✅"
    elif score >= 50:
        return "Good ⚡"
    else:
        return "Needs Improvement ❌"

# Function to check resume length
def check_resume_length(text):
    word_count = len(text.split())
    if word_count < 300:
        return "Too short ❌"
    elif word_count > 1000:
        return "Too long ⚠️"
    else:
        return "Good length ✅"

# Function to generate score explanation
def get_score_explanation(score, keywords_list, resume_text):
    if not keywords_list:
        return "No keywords provided for evaluation."
    keyword_matches = sum(keyword.lower() in resume_text.lower() for keyword in keywords_list)
    if score >= 80:
        return f"Excellent match! Score: {score}%. Found {keyword_matches} relevant keywords."
    elif score >= 50:
        return f"Good match. Score: {score}%. Found {keyword_matches} relevant keywords."
    else:
        return f"Needs improvement. Score: {score}%. Found {keyword_matches} relevant keywords."

# Function to rank resumes
def rank_resumes(job_description, resumes):
    documents = [job_description] + resumes
    vectorizer = TfidfVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()
    job_description_vector = vectors[0]
    resume_vectors = vectors[1:]
    cosine_similarities = cosine_similarity([job_description_vector], resume_vectors).flatten()

    # Apply experience-based weighting
    experience_weights = {
        "Entry-level": 1.0,
        "Mid-level": 1.2,
        "Senior": 1.5,
        "Unknown": 1.0
    }
    experience_levels = [extract_experience(resume) for resume in resumes]
    weighted_scores = cosine_similarities * np.array([experience_weights[level] for level in experience_levels])

    return weighted_scores

# Function to save feedback to a JSON file
def save_feedback(name, email, feedback):
    feedback_data = {
        "name": name,
        "email": email,
        "feedback": feedback,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current time
    }

    # Load existing feedback or create a new list
    try:
        with open("feedback.json", "r") as file:
            feedback_list = json.load(file)
    except FileNotFoundError:
        feedback_list = []

    # Append new feedback
    feedback_list.append(feedback_data)

    # Save updated feedback list to JSON file
    with open("feedback.json", "w") as file:
        json.dump(feedback_list, file, indent=4)

# Streamlit app
st.title("AI Resume Screening & Candidate Ranking System")

# Job description input
st.header("Job Description")
job_description = st.text_area("Enter the job description")

# Job title input
job_title = st.text_input("Enter the job title")
st.write(f"Job Title: {job_title}")

# Keywords input
skills_keywords = st.text_input("Enter specific skills or keywords (comma-separated)")
keywords_list = [kw.strip() for kw in skills_keywords.split(",")] if skills_keywords else []

# File uploader
st.header("Upload Resumes")
uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

# Check file size
if uploaded_files:
    for file in uploaded_files:
        if file.size > MAX_FILE_SIZE:
            st.error(f"File {file.name} exceeds the 2MB size limit. Please upload a smaller file.")
            uploaded_files = []  # Clear the list to prevent processing
            break

# Check upload limit
if uploaded_files and len(uploaded_files) > 10:
    st.error("You can upload a maximum of 10 resumes at once.")

# Progress bar
progress_bar = st.progress(0)

# Process resumes
if uploaded_files and job_description:
    st.header("Ranking Resumes")
    resumes = []
    for i, file in enumerate(uploaded_files):
        text = extract_text_from_pdf(file)
        resumes.append(text)
        progress_bar.progress((i + 1) / len(uploaded_files))

    # Rank resumes
    start_time = time.time()
    scores = np.round(rank_resumes(job_description, resumes) * 100, 2)
    end_time = time.time()
    ranking_time = end_time - start_time

    # Extract contact info
    contact_info = [extract_contact_info(text) for text in resumes]

    # Create DataFrame
    results = pd.DataFrame({
        "Resume": [file.name for file in uploaded_files],
        "Score": scores,  # Scores are already floats
        "Rank": [get_rank_label(score) for score in scores],
        "Resume Length Feedback": [check_resume_length(text) for text in resumes],
        "Email": [info["Email"] for info in contact_info],
        "Phone": [info["Phone"] for info in contact_info],
    })

    # Add explanation column
    results["Explanation"] = [
        get_score_explanation(score, keywords_list, resumes[i])
        for i, score in enumerate(results["Score"])
    ]
    results["Experience Level"] = [extract_experience(text) for text in resumes]

    # Sort results
    results = results.sort_values(by="Score", ascending=False)

    # Display ranking time
    st.write(f"Ranking completed in {ranking_time:.2f} seconds")

    # Filter by experience level
    experience_level = st.selectbox("Filter by experience level", ["All", "Entry-level", "Mid-level", "Senior"])
    if experience_level != "All":
        filtered_results = results[results["Experience Level"] == experience_level]
        st.write(filtered_results)
    else:
        st.write(results)

    # Display top 3 resumes
    st.header("Top 3 Resumes")
    top_3 = results.head(3)
    st.write(top_3)

    # Visualize scores using Seaborn
    st.header("Resume Scores Visualization")
    sorted_results = results.sort_values(by="Score", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(y=sorted_results["Resume"], x=sorted_results["Score"], palette="Blues_r", ax=ax)
    ax.set_xlabel("Score (%)")
    ax.set_ylabel("Resumes")
    ax.set_title("Resume Ranking Scores")
    ax.set_xlim(0, 100)
    for i in ax.containers:
        ax.bar_label(i, fmt='%.1f%%', label_type="edge", fontsize=10)
    st.pyplot(fig)

    # Check for duplicates
    duplicates = check_duplicates(resumes)
    if duplicates:
        st.write("Duplicate Resumes:", duplicates)
    else:
        st.write("No duplicate resumes found.")

    # Download results
    csv = results.to_csv(index=False)
    st.download_button("Download Results", csv, file_name="ranked_resumes.csv", mime="text/csv")

    # Feedback section
    st.header("Feedback")
    name = st.text_input("Enter your name")
    email = st.text_input("Enter your email")
    feedback = st.text_area("Provide feedback or suggestions")
    if st.button("Submit Feedback"):
        if name and email and feedback:  # Ensure all fields are filled
            save_feedback(name, email, feedback)
            st.success("Thank you for your feedback!")
        else:
            st.error("Please fill in all fields (name, email, and feedback).")