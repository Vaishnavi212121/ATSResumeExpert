import streamlit as st
import os
import io
import fitz  # PyMuPDF
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("Missing Google API Key. Please check your .env file.")
else:
    genai.configure(api_key=api_key)

def get_gemini_response(prompt, pdf_content, job_description):
    """
    Calls Gemini model with instructions, resume data, and job description.
    """
    model = genai.GenerativeModel('gemini-1.5-flash') # Using stable 1.5 Flash
    # The content list should be: [System Prompt, Image/File, User Job Description]
    response = model.generate_content([prompt, pdf_content[0], job_description])
    return response.text

def input_pdf_setup(uploaded_file):
    """
    Converts PDF pages into images for Gemini processing.
    """
    if uploaded_file is not None:
        # Read the PDF using PyMuPDF (no Poppler required)
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        
        pdf_parts = []
        for page_index in range(len(doc)):
            page = doc.load_page(page_index)
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("jpeg")
            
            # Append as Gemini-compatible part
            pdf_parts.append({
                "mime_type": "image/jpeg",
                "data": img_bytes 
            })
            
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# --- Streamlit UI ---
st.set_page_config(page_title="ATS Resume Expert", layout="wide")

st.markdown("""
    # 📄 ATS Resume Expert
    ### Optimize your resume for Gemini-powered AI screening
""")

col1, col2 = st.columns([1, 1])

with col1:
    job_description = st.text_area("Paste Job Description:", height=300)
    uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])

with col2:
    st.info("Choose an action below to analyze your resume.")
    submit_analysis = st.button("🔍 Detailed Review")
    submit_match = st.button("📊 Percentage Match")

# --- Prompts ---
prompt_review = """
You are an experienced Technical HR Manager. Review this resume against the job description. 
Provide a professional evaluation including:
1. Candidate Suitability.
2. Key Strengths.
3. Critical Gaps/Weaknesses.
4. Recommendations for improvement.
"""

prompt_ats = """
You are an advanced ATS Scanner. Compare the resume to the job description.
Return the output in this format:
- Match Percentage: [X]%
- Missing Keywords: [List]
- Final Assessment: [Brief summary]
"""

# --- Execution ---
if (submit_analysis or submit_match) and uploaded_file and job_description:
    with st.spinner("Analyzing..."):
        try:
            pdf_content = input_pdf_setup(uploaded_file)
            current_prompt = prompt_review if submit_analysis else prompt_ats
            
            response = get_gemini_response(current_prompt, pdf_content, job_description)
            
            st.divider()
            st.subheader("Analysis Results")
            st.markdown(response)
        except Exception as e:
            st.error(f"Error processing request: {e}")
elif (submit_analysis or submit_match):
    st.warning("Please provide both a job description and a resume.")
