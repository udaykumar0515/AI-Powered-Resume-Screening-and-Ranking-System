# AI-Powered-Resume-Screening-and-Ranking-System
An AI-driven tool that automates resume screening using TF-IDF, Cosine Similarity, and NLP. It ranks resumes based on job descriptions, detects duplicates, extracts contact info, and provides visual insights. Built with Python, Streamlit, and Scikit-learn.

### **How to Use This?**  
1. Replace `"your-username"` in the GitHub link with your actual GitHub username.  
2. Rename `"app.py"` if your file has a different name.  
3. Update the **Future Improvements** section based on what you plan to add.  
# AI-Powered Resume Screening & Ranking System  

An AI-driven web application that automates the process of **resume screening and ranking** based on job descriptions. The system extracts **text from PDFs**, applies **Natural Language Processing (NLP) techniques**, and ranks resumes using **TF-IDF vectorization and cosine similarity**.  

## 🚀 Features  
- **Automated Resume Ranking** – Uses **TF-IDF & Cosine Similarity** for job-resume matching.  
- **Experience-Based Weighting** – Adjusts ranking based on **entry-level, mid-level, and senior experience**.  
- **Duplicate Resume Detection** – Prevents multiple submissions of the same resume.  
- **Resume Length Analysis** – Provides feedback on whether a resume is **too short or too long**.  
- **Contact Information Extraction** – Automatically extracts **emails and phone numbers** from resumes.  
- **Keyword Matching** – Allows recruiters to enter **specific skills** to refine rankings.  
- **Data Visualization** – Displays **resume score distributions** using Seaborn and Matplotlib.  
- **User Feedback Collection** – Allows users to submit feedback, stored in a **JSON file**.  

## 🛠️ Technologies Used  
- **Python** – Main programming language  
- **Streamlit** – Web interface  
- **Scikit-learn** – Machine learning (TF-IDF, Cosine Similarity)  
- **PyPDF2** – Extracting text from PDF resumes  
- **Pandas & NumPy** – Data handling  
- **Seaborn & Matplotlib** – Data visualization  
- **JSON** – Storing user feedback  

## 📂 Project Structure  
📁 ai_resume_screening
┣ 📜 app.py # Main Streamlit application
┣ 📜 requirements.txt # Dependencies list
┣ 📜 feedback.json # Stores collected user feedback
┣ 📁 sample_resumes # Folder for testing resumes
┗ 📜 README.md # Project documentation
