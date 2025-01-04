import requests
from bs4 import BeautifulSoup
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient
import ast
import re
import json
import re
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class TextCleaner:
    @staticmethod
    def clean_markdown(text):
        # Remove markdown bold markers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        
        # Convert markdown sections into structured data
        use_cases = []
        current_use_case = {}
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("Use Case"):
                if current_use_case:
                    use_cases.append(current_use_case)
                current_use_case = {"title": line}
            elif line.startswith("Objective:"):
                current_use_case["objective"] = line[10:].strip()
            elif line.startswith("AI Application:"):
                current_use_case["application"] = line[14:].strip()
            elif line.startswith("Cross-Functional Benefits:"):
                current_use_case["benefits"] = []
            elif line.startswith("-") and "benefits" in current_use_case:
                benefit = line[1:].strip()
                current_use_case["benefits"].append(benefit)
            elif line.startswith("Keywords:"):
                current_use_case["keywords"] = line[9:].strip()
                
        if current_use_case:
            use_cases.append(current_use_case)
            
        return use_cases
    def clean_company_analysis(text):
        # Remove markdown bold markers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        
        # Parse company analysis into structured sections
        sections = {
            "offerings": [],
            "focus_areas": [],
            "vision_goals": "",
            "industry": ""
        }
        
        current_section = None
        current_text = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "Key offerings" in line or "Offerings:" in line:
                current_section = "offerings"
            elif "Strategic focus" in line or "Focus Areas:" in line:
                if current_section and current_text:
                    sections[current_section] = current_text
                current_section = "focus_areas"
                current_text = []
            elif "Vision" in line or "Goals:" in line:
                if current_section and current_text:
                    sections[current_section] = current_text
                current_section = "vision_goals"
                current_text = []
            elif "Industry" in line or "Market segment:" in line:
                if current_section and current_text:
                    sections[current_section] = current_text
                current_section = "industry"
                current_text = []
            elif line.startswith("-") or line.startswith("•"):
                current_text.append(line[1:].strip())
            elif current_section:
                current_text.append(line)
        
        if current_section and current_text:
            sections[current_section] = current_text
            
        return sections

    @staticmethod
    def clean_competitor_analysis(text):
        # Remove markdown bold markers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        
        # Parse competitor analysis into structured sections
        sections = {
            "market_trends": [],
            "drivers_challenges": [],
            "forecasts": [],
            "industry_reports": [],
            "competitors": {}
        }
        
        current_section = None
        current_competitor = None
        current_text = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "Market trends" in line or "Overview:" in line:
                current_section = "market_trends"
                current_competitor = None
            elif "Drivers" in line or "Challenges:" in line:
                if current_section and current_text:
                    sections[current_section] = current_text
                current_section = "drivers_challenges"
                current_text = []
            elif "Forecast" in line or "Growth:" in line:
                if current_section and current_text:
                    sections[current_section] = current_text
                current_section = "forecasts"
                current_text = []
            elif "Industry" in line or "Reports:" in line:
                if current_section and current_text:
                    sections[current_section] = current_text
                current_section = "industry_reports"
                current_text = []
            elif line.startswith("Company:") or line.endswith(":"):
                if current_section and current_text:
                    sections[current_section] = current_text
                current_section = "competitors"
                current_competitor = line.replace("Company:", "").replace(":", "").strip()
                sections["competitors"][current_competitor] = []
                current_text = []
            elif line.startswith("-") or line.startswith("•"):
                if current_competitor:
                    sections["competitors"][current_competitor].append(line[1:].strip())
                else:
                    current_text.append(line[1:].strip())
            elif current_section:
                if current_competitor:
                    sections["competitors"][current_competitor].append(line)
                else:
                    current_text.append(line)
        
        if current_section and current_text:
            sections[current_section] = current_text
            
        return sections
class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        # Main heading style
        self.styles.add(ParagraphStyle(
            name='MainHeading',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            textColor=colors.HexColor('#1B4F72'),
            leading=24
        ))
        
        # Use case title style
        self.styles.add(ParagraphStyle(
            name='UseCaseTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            textColor=colors.HexColor('#2874A6'),
            leading=20
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.HexColor('#2E86C1'),
            leading=16
        ))
        
        
        # Benefit text style
        self.styles.add(ParagraphStyle(
            name='BenefitText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=20,
            leading=14
        ))
        
        # Keywords style
        self.styles.add(ParagraphStyle(
            name='Keywords',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=20,
            textColor=colors.HexColor('#566573'),
            leading=14
        ))
        self.styles.add(ParagraphStyle(
            name='AnalysisSection',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#2874A6'),
            leading=18
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            textColor=colors.HexColor('#566573'),
            leading=16
        ))
        
        self.styles.add(ParagraphStyle(
            name='AnalysisList',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=20,
            leading=14
        ))

    def create_company_analysis_pdf(self, company_analysis, competitor_analysis, filename="company_analysis.pdf"):
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        story = []
        
        # Company Analysis Section
        story.append(Paragraph("Company Analysis", self.styles['MainHeading']))
        
        # Key Offerings
        if company_analysis["offerings"]:
            story.append(Paragraph("Key Offerings and Services", self.styles['AnalysisSection']))
            for offering in company_analysis["offerings"]:
                story.append(Paragraph(f"• {offering}", self.styles['AnalysisList']))
            story.append(Spacer(1, 12))
        
        # Strategic Focus Areas
        if company_analysis["focus_areas"]:
            story.append(Paragraph("Strategic Focus Areas", self.styles['AnalysisSection']))
            for focus in company_analysis["focus_areas"]:
                story.append(Paragraph(f"• {focus}", self.styles['AnalysisList']))
            story.append(Spacer(1, 12))
        
        # Vision and Goals
        if company_analysis["vision_goals"]:
            story.append(Paragraph("Vision and Goals", self.styles['AnalysisSection']))
            for goal in company_analysis["vision_goals"]:
                story.append(Paragraph(goal, self.styles['BodyText']))
            story.append(Spacer(1, 12))
        
        # Industry
        if company_analysis["industry"]:
            story.append(Paragraph("Industry and Market Segment", self.styles['AnalysisSection']))
            for ind in company_analysis["industry"]:
                story.append(Paragraph(ind, self.styles['BodyText']))
        
        story.append(Spacer(1, 30))
        
        # Competitor Analysis Section
        story.append(Paragraph("Market & Competitor Analysis", self.styles['MainHeading']))
        
        # Market Trends
        if competitor_analysis["market_trends"]:
            story.append(Paragraph("Market Trends in AI", self.styles['AnalysisSection']))
            for trend in competitor_analysis["market_trends"]:
                story.append(Paragraph(f"• {trend}", self.styles['AnalysisList']))
            story.append(Spacer(1, 12))
        
        # Drivers and Challenges
        if competitor_analysis["drivers_challenges"]:
            story.append(Paragraph("Key Drivers and Challenges", self.styles['AnalysisSection']))
            for item in competitor_analysis["drivers_challenges"]:
                story.append(Paragraph(f"• {item}", self.styles['AnalysisList']))
            story.append(Spacer(1, 12))
        
        # Market Forecasts
        if competitor_analysis["forecasts"]:
            story.append(Paragraph("Market Forecasts and Growth Potential", self.styles['AnalysisSection']))
            for forecast in competitor_analysis["forecasts"]:
                story.append(Paragraph(forecast, self.styles['BodyText']))
            story.append(Spacer(1, 12))
        
        # Competitor Details
        if competitor_analysis["competitors"]:
            story.append(Paragraph("Competitor Analysis", self.styles['AnalysisSection']))
            for company, details in competitor_analysis["competitors"].items():
                story.append(Paragraph(company, self.styles['CompanyName']))
                for detail in details:
                    story.append(Paragraph(f"• {detail}", self.styles['AnalysisList']))
                story.append(Spacer(1, 8))
        
        # Industry Reports
        if competitor_analysis["industry_reports"]:
            story.append(Paragraph("Industry Reports and Insights", self.styles['AnalysisSection']))
            for report in competitor_analysis["industry_reports"]:
                story.append(Paragraph(f"• {report}", self.styles['AnalysisList']))
        
        doc.build(story)

    def create_use_cases_pdf(self, use_cases_data, dataset_links, filename="use_cases.pdf"):
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        story = []
        
        # Main heading
        story.append(Paragraph("AI Use Cases & Implementation Resources", self.styles['MainHeading']))
        
        # Process each use case
        for use_case in use_cases_data:
            # Use case title
            story.append(Paragraph(use_case['title'], self.styles['UseCaseTitle']))
            
            # Objective
            story.append(Paragraph("Objective:", self.styles['SectionHeading']))
            story.append(Paragraph(use_case['objective'], self.styles['BodyText']))
            
            # AI Application
            story.append(Paragraph("AI Application:", self.styles['SectionHeading']))
            story.append(Paragraph(use_case['application'], self.styles['BodyText']))
            
            # Benefits
            story.append(Paragraph("Cross-Functional Benefits:", self.styles['SectionHeading']))
            for benefit in use_case['benefits']:
                story.append(Paragraph(f"• {benefit}", self.styles['BenefitText']))
            
            # Keywords
            story.append(Paragraph(f"Keywords: {use_case['keywords']}", self.styles['Keywords']))
            
            # Dataset links for this use case
            if use_case['title'] in dataset_links:
                links = dataset_links[use_case['title']]
                story.append(Paragraph("Implementation Resources:", self.styles['SectionHeading']))
                
                if links["github_links"]:
                    for link in links["github_links"]:
                        story.append(Paragraph(f"• GitHub: {link}", self.styles['BodyText']))
                
                if links["kaggle_links"]:
                    for link in links["kaggle_links"]:
                        story.append(Paragraph(f"• Kaggle: {link}", self.styles['BodyText']))
                
                if links["huggingface_links"]:
                    for link in links["huggingface_links"]:
                        story.append(Paragraph(f"• Hugging Face: {link}", self.styles['BodyText']))
            
            story.append(Spacer(1, 20))
        
        doc.build(story)

class WebsiteAnalyzer:
    def __init__(self, tavily_api_key, serper_api_key, google_api_key):
        self.tavily_client = TavilyClient(api_key=tavily_api_key)
        self.serper_api_key = serper_api_key
        os.environ["GOOGLE_API_KEY"] = google_api_key
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
        self.pdf_generator = PDFGenerator()
        self.text_cleaner = TextCleaner()



    def analyze_and_generate_pdfs(self, website_url):
        footer_content = self.get_footer_content(website_url)
        company_analysis_raw = self.llm.invoke(self._generate_company_analysis_prompt(footer_content, [])).content
        _, competitor_analysis_raw = self.get_competitor_analysis(website_url)
        
        # Call static methods directly using the class name
        company_analysis = TextCleaner.clean_company_analysis(company_analysis_raw)  # Changed
        competitor_analysis = TextCleaner.clean_competitor_analysis(competitor_analysis_raw)  # Changed
        
        # Get use cases and clean the output
        use_cases_response = self.llm.invoke(self._generate_use_cases_prompt(company_analysis_raw, competitor_analysis_raw))
        use_cases_data = TextCleaner.clean_markdown(use_cases_response.content)  # Changed

        
       
        
        # Get dataset links
        use_case_links = {}
        for use_case in use_cases_data:
            keywords = use_case.get('keywords', '').split(', ')
            keywords_str = " ".join(keywords)
            dataset_links = self.get_dataset_links(keywords_str)
            use_case_links[use_case['title']] = dataset_links
        
        # Generate PDFs
        self.pdf_generator.create_company_analysis_pdf(company_analysis, competitor_analysis)
        self.pdf_generator.create_use_cases_pdf(use_cases_data, use_case_links)
        
        return "PDFs generated successfully: company_analysis.pdf and use_cases.pdf"


    def get_footer_content(self, website_url):
        try:
            response = requests.get(website_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            footer = soup.find("footer")
            if not footer:
                return None

            links = footer.find_all("a", href=True)
            footer_links = [{"text": link.get_text(strip=True), "url": link["href"]} for link in links]
            
            footer_content = {}
            for link in footer_links:
                url = link["url"]
                full_url = requests.compat.urljoin(website_url, url)
                try:
                    link_response = requests.get(full_url)
                    link_response.raise_for_status()
                    link_soup = BeautifulSoup(link_response.content, "html.parser")
                    page_text = link_soup.get_text(separator="\n", strip=True)
                    footer_content[full_url] = page_text
                except Exception as e:
                    footer_content[full_url] = f"Failed to fetch content: {str(e)}"

            return self._combine_footer_content(footer_content)
        except Exception as e:
            return f"Error fetching footer content: {str(e)}"

    def _combine_footer_content(self, footer_content):
        combined_content = ""
        for url, content in footer_content.items():
            combined_content += f"\n\nURL: {url}\nContent:\n{content}"
        return combined_content

    def get_competitors(self, website):
        answer = self.tavily_client.qna_search(query=f"List 5 competitors to {website} in an array")
        try:
            return ast.literal_eval(answer)
        except Exception as e:
            print(f"Error parsing competitors: {e}")
            return []

    def get_dataset_links(self, keywords):
        url = "https://google.serper.dev/search"
        payload = json.dumps({
            "q": f"provide kaggle/hugging face datasets related to topic {keywords}",
            "gl": "in"
        })
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()
            
            links = {"github_links": [], "kaggle_links": [], "huggingface_links": []}
            for result in data.get('organic', []):
                if 'github.com' in result['link']:
                    links["github_links"].append(result['link'])
                elif 'kaggle.com' in result['link']:
                    links["kaggle_links"].append(result['link'])
                elif 'huggingface.co' in result['link']:
                    links["huggingface_links"].append(result['link'])
            return links
        except Exception as e:
            print(f"Error fetching dataset links: {e}")
            return {"github_links": [], "kaggle_links": [], "huggingface_links": []}

    def extract_use_cases(self, response_text):
        use_case_keywords = {}
        matches = re.findall(
            r'\*\*Use Case \d+: (.*?)\*\*.*?\*\*Keywords:\*\* (.*?)\n',
            response_text,
            re.DOTALL
        )
        for match in matches:
            use_case = match[0].strip()
            keywords = [keyword.strip() for keyword in match[1].split(',')]
            use_case_keywords[use_case] = keywords
        return use_case_keywords

    def analyze_website(self, website_url):
        # Step 1: Get website footer content
        footer_content = self.get_footer_content(website_url)
        
        # Step 2: Get competitors
        competitors_analysis_prompt = self.get_competitor_analysis(website_url)
        competitors_analysis = self.llm.invoke(competitors_analysis_prompt)
        competitors = self.get_competitors(website_url)
        
        # Step 3: Generate company analysis
        company_analysis_prompt = self._generate_company_analysis_prompt(footer_content, competitors)
        company_analysis = self.llm.invoke(company_analysis_prompt)
        
        # Step 4: Generate use cases
        use_cases_prompt = self._generate_use_cases_prompt(company_analysis.content,competitors_analysis)
        use_cases_response = self.llm.invoke(use_cases_prompt)
        
        # Step 5: Extract use cases and get dataset links
        use_case_keywords = self.extract_use_cases(use_cases_response.content)
        use_case_links = {}
        
        for use_case, keywords in use_case_keywords.items():
            keywords_str = " ".join(keywords)
            dataset_links = self.get_dataset_links(keywords_str)
            use_case_links[use_case] = dataset_links
        
        return {
            "company_analysis": company_analysis.content,
            "use_cases": use_cases_response.content,
            "dataset_links": use_case_links
        }

    def _generate_company_analysis_prompt(self, footer_content, website_url):
        return f"""
        Based on the following content extracted from {website_url}, provide a detailed analysis:
        
        Content:
        {footer_content}
        
        
        Please analyze:
        1. Products and services
        2. Strategic focus areas
        3. Vision and goals
        4. Industry and market segment


        """

    def _generate_use_cases_prompt(self, company_analysis, competitors):
        return f"""
        As an AIML expert, propose relevant use cases where the company can leverage GenAI, LLMs, and ML technologies.
        add references (links) through which certain use cases were suggested
        Company Analysis:
        {company_analysis}
        
        Competitors:
        {competitors}
        
        Format each use case as follows:
        **Use Case X: [Title]**
        Objective: [Description]
        AI Application: [Details]
        Cross-Functional Benefits:
        - [Benefit 1]
        - [Benefit 2]
        **Keywords:** [keyword1], [keyword2], [keyword3]
        """


    def get_competitor_analysis(self, website_url):
        try:
            answer = self.tavily_client.qna_search(query=f"List 5 competitors to {website_url} in an array")
            competitor_names = ast.literal_eval(answer)
        except Exception as e:
            print("Error in parsing the competitor data:", e)
            competitor_names = []

        prompt = f"""
        List down company-wise their products and services offered in detail.
        Competitors: {competitor_names}

        Provide market analysis, including:
        1. Overview of market trends in AI.
        2. Drivers and challenges in the AI landscape.
        3. Market forecasts and growth potential.
        4. Industry-specific reports from McKinsey or Deloitte.(if not found then leave)
        """
        response = self.llm.invoke(prompt)
        return competitor_names, response.content
