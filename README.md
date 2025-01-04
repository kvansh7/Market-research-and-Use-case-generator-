# Website AI Analysis Tool

A Streamlit application that analyzes websites and generates detailed AI use case reports using various AI services including Google's Gemini Pro, Tavily, and Serper.

## Features

- Website footer content analysis
- Competitor analysis
- AI use case generation
- PDF report generation (Company Analysis and Use Cases)
- Combined report download functionality

## Prerequisites

- Python 3.10 or higher
- Required API keys:
  - Google API key (Gemini Pro)
  - Tavily API key
  - Serper API key

## Installation

1. Clone the repository
```bash
git clone https://github.com/kvansh7/Market-research-and-Use-case-generator-.git
```

2. Create a virtual environment (recommended)
```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```
TAVILY_API_KEY=your_tavily_api_key_here
SERPER_API_KEY=your_serper_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL displayed in the terminal (typically `http://localhost:8501`)

3. Enter a website URL and click "Analyze Website"

4. Once analysis is complete, download the generated reports using the "Download All Reports" button

## Project Structure

```
website-analysis-tool/
├── app.py                 # Main Streamlit application
├── website_analyzer.py    # Core analysis functionality
├── requirements.txt       # Python dependencies
├── .env                  # API keys (not tracked in git)
└── README.md             # This file
```

## Dependencies

- streamlit
- python-dotenv
- beautifulsoup4
- langchain
- langchain-google-genai
- tavily-python
- reportlab
- requests
