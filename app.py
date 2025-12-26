import sys
import os
import streamlit as st

from lib.groq_handler import GroqHandler
from lib.text_processor import Textprocessor
from lib.resume_analyzer import ResumeAnalyzer
from utils.file_utils import save_text_to_file, remove_files
from utils.logger import setup_logger
from utils.config import Config
from utils.prompt_loader import Promptloader

# --------------------------
# Logger Setup
# --------------------------
if 'loggers' not in st.session_state:
    st.session_state.loggers = {
        "app": setup_logger("app", f"{Config.LOG_DIR}/app.log"),
        "groq_handler": setup_logger("groq_handler", f"{Config.LOG_DIR}/groq_handler.log"),
        "prompt_loader": setup_logger("prompt_loader", f"{Config.LOG_DIR}/prompt_loader.log"),
        "resume_analyzer": setup_logger("resume_analyzer", f"{Config.LOG_DIR}/resume_analyzer.log"),
        "text_processor": setup_logger("text_processor", f"{Config.LOG_DIR}/text_processor.log")
    }
    st.session_state.loggers["app"].debug("Starting Resume Analyzer application")

loggers = st.session_state.loggers

# --------------------------
# Initialize components (cached)
# --------------------------
@st.cache_resource
def get_groq_handler():
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in Streamlit secrets")
    return GroqHandler(loggers["groq_handler"], Promptloader(Config.PROMPTS_FILE, loggers["prompt_loader"]), api_key=api_key)

@st.cache_resource
def get_text_processor():
    return Textprocessor(loggers["text_processor"])

@st.cache_resource
def get_resume_analyzer(_grok_handler):
    return ResumeAnalyzer(_grok_handler, loggers["resume_analyzer"], Promptloader(Config.PROMPTS_FILE, loggers["prompt_loader"]))

grok_handler = get_groq_handler()
text_processor = get_text_processor()
resume_analyzer = get_resume_analyzer(grok_handler)

# --------------------------
# Main Streamlit app
# --------------------------
def main():
    if 'page' not in st.session_state:
        st.session_state.page = "upload"
    if 'analysis' not in st.session_state:
        st.session_state.analysis = None
    if 'processed' not in st.session_state:
        st.session_state.processed = False

    # --------------------------
    # Upload Page
    # --------------------------
    if st.session_state.page == "upload":
        st.title("Resume Analyzer")
        st.subheader("Upload a PDF or Word Resume")

        uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])
        col1, col2, col3 = st.columns(3)

        with col1:
            designation = st.selectbox("Select Desired Designation", ["Data Scientist", "Data Analyst", "MLOps Engineer"])
        with col2:
            experience = st.selectbox("Select Experience Level", ["Fresher", "1-3 Year Experience", "3-5 Years Experience", "5-8 Years Experience"])
        with col3:
            domain = st.selectbox("Select Domain", ["None", "Finance", "Healthcare", "Automobile", "Real Estate"])

        if st.button("Analyze") and uploaded_file:
            loggers["app"].debug("User clicked Analyze button for file: %s", uploaded_file.name)
            st.session_state.uploaded_file = uploaded_file
            st.session_state.designation = designation
            st.session_state.experience = experience
            st.session_state.domain = domain
            st.session_state.page = "results"
            st.session_state.processed = False
            st.experimental_rerun()

    # --------------------------
    # Results Page
    # --------------------------
    elif st.session_state.page == "results":
        uploaded_file = st.session_state.uploaded_file
        file_extension = uploaded_file.name.split(".")[-1].lower()
        temp_path = f"temp_resume.{file_extension}"

        try:
            if not st.session_state.processed:
                loggers["app"].debug("Processing uploaded file: %s", uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                extracted_text = text_processor.extract_text(temp_path, file_extension)
                remove_files(temp_path)

                if extracted_text:
                    loggers["app"].debug("Text extracted successfully, length: %d characters", len(extracted_text))
                    with st.spinner("Analyzing resume... Please wait"):
                        st.session_state.analysis = resume_analyzer.analyze_resume(
                            extracted_text, st.session_state.designation, st.session_state.experience, st.session_state.domain
                        )
                        st.session_state.processed = True
                    loggers["app"].debug("Resume analysis completed")
                else:
                    st.error("Could not extract text. Please check the file format.")
                    loggers["app"].error("Failed to extract text from %s", uploaded_file.name)

            if st.session_state.analysis:
                if st.button("Upload New Resume"):
                    loggers["app"].debug("User clicked Upload New Resume")
                    st.session_state.page = "upload"
                    st.session_state.analysis = None
                    st.session_state.processed = False
                    st.experimental_rerun()

                st.markdown("# Resume Analysis")
                st.write(st.session_state.analysis)

                output_filename = "resume_analysis.txt"
                save_text_to_file(st.session_state.analysis, output_filename)
                with open(output_filename, "rb") as file:
                    st.download_button(label="Download Analysis", data=file, file_name=output_filename, mime="text/plain")
                remove_files(output_filename)

        except Exception as e:
            loggers["app"].error("Error processing resume: %s", str(e))
            st.error(f"Error processing resume: {str(e)}")
            remove_files(temp_path)

if __name__ == "__main__":
    main()
