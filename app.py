# app.py
import streamlit as st
import os
from dotenv import load_dotenv
from website_analyzer import WebsiteAnalyzer
import zipfile
import io

# Load environment variables
load_dotenv()

def create_zip_file():
    """Create a zip file containing both PDFs"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        # Add both PDFs to the zip file if they exist
        if os.path.exists("company_analysis.pdf"):
            zip_file.write("company_analysis.pdf")
        if os.path.exists("use_cases.pdf"):
            zip_file.write("use_cases.pdf")
    
    zip_buffer.seek(0)
    return zip_buffer

def main():
    st.title("Website AI Analysis Tool")
    st.write("Analyze websites and generate AI use cases with detailed reports")

    # Get API keys from environment variables
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    serper_api_key = os.getenv("SERPER_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")

    if not tavily_api_key or not serper_api_key or not google_api_key:
        st.error("Please set up all required API keys in the .env file")
        return

    # Create analyzer instance
    analyzer = WebsiteAnalyzer(
        tavily_api_key=tavily_api_key,
        serper_api_key=serper_api_key,
        google_api_key=google_api_key
    )

    # Store the analysis state
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False

    # Input field for website URL
    website_url = st.text_input("Enter website URL:",)

    if st.button("Analyze Website"):
        with st.spinner("Analyzing website and generating reports..."):
            try:
                result = analyzer.analyze_and_generate_pdfs(website_url)
                st.success(result)
                st.session_state.analysis_complete = True
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.session_state.analysis_complete = False

    # Single download button for both PDFs
    if st.session_state.analysis_complete:
        if os.path.exists("company_analysis.pdf") and os.path.exists("use_cases.pdf"):
            zip_buffer = create_zip_file()
            st.download_button(
                label="Download All Reports",
                data=zip_buffer,
                file_name="website_analysis_reports.zip",
                mime="application/zip",
            )

if __name__ == "__main__":
    main()