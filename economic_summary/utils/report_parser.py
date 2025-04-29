"""
Utility for parsing economic reports from various sources.
"""
import logging
import requests
from bs4 import BeautifulSoup
import re
import io
import PyPDF2
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class ReportParser:
    """
    Parser for economic reports from various sources.
    Supports HTML and PDF parsing.
    """
    
    def __init__(self):
        """Initialize the report parser."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        })
    
    def get_report_content(self, url, max_content_length=500):
        """
        Get the content of a report from a URL.
        
        Args:
            url: URL of the report
            max_content_length: Maximum content length to return (default: 500 chars)
            
        Returns:
            str: Report content excerpt
        """
        try:
            if not url:
                return "No URL provided"
                
            # Check if it's a PDF
            if url.lower().endswith('.pdf'):
                return self._parse_pdf(url, max_content_length)
            else:
                return self._parse_html(url, max_content_length)
        except Exception as e:
            logger.error(f"Error getting report content from {url}: {str(e)}")
            return f"Error retrieving content: {str(e)}"
    
    def _parse_html(self, url, max_content_length=500):
        """
        Parse HTML content from a URL.
        
        Args:
            url: URL of the HTML page
            max_content_length: Maximum content length to return (default: 500 chars)
            
        Returns:
            str: Extracted text content
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Extract only the beginning of the content
            if len(text) > max_content_length:
                text = text[:max_content_length] + "..."
                
            return text
        except Exception as e:
            logger.error(f"Error parsing HTML from {url}: {str(e)}")
            return f"Error parsing HTML: {str(e)}"
    
    def _parse_pdf(self, url, max_content_length=500):
        """
        Parse PDF content from a URL.
        
        Args:
            url: URL of the PDF
            max_content_length: Maximum content length to return (default: 500 chars)
            
        Returns:
            str: Extracted text content
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Read PDF content
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from only the first page
            text = ""
            if len(pdf_reader.pages) > 0:
                page = pdf_reader.pages[0]
                text = page.extract_text()
            
            # Truncate if needed
            if len(text) > max_content_length:
                text = text[:max_content_length] + "..."
                
            return text
        except Exception as e:
            logger.error(f"Error parsing PDF from {url}: {str(e)}")
            return f"Error parsing PDF: {str(e)}"
    
    def extract_links_from_page(self, url, pdf_only=False):
        """
        Extract links from a webpage.
        
        Args:
            url: URL of the webpage
            pdf_only: Whether to only return PDF links
            
        Returns:
            list: List of links
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(url, href)
                
                if pdf_only and not full_url.lower().endswith('.pdf'):
                    continue
                    
                links.append({
                    'url': full_url,
                    'text': a_tag.get_text(strip=True)
                })
                
            return links
        except Exception as e:
            logger.error(f"Error extracting links from {url}: {str(e)}")
            return []
    
    def rank_reports_by_importance(self, reports, keywords=None):
        """
        Rank reports by importance based on keywords and other factors.
        
        Args:
            reports: List of report dictionaries with 'name', 'link', etc.
            keywords: List of keywords to look for
            
        Returns:
            list: Ranked list of reports
        """
        if not keywords:
            keywords = [
                'inflation', 'gdp', 'unemployment', 'interest rate', 'federal reserve',
                'monetary policy', 'recession', 'economic outlook', 'fomc', 'cpi'
            ]
            
        # Score each report
        scored_reports = []
        for report in reports:
            score = 0
            name = report.get('name', '').lower()
            
            # Score based on keywords in name
            for keyword in keywords:
                if keyword.lower() in name:
                    score += 5
            
            # Score based on recency (if available)
            if 'press_release' in report and report['press_release']:
                score += 3
                
            # Add the report with its score
            scored_reports.append({
                'report': report,
                'score': score
            })
            
        # Sort by score (descending)
        sorted_reports = sorted(scored_reports, key=lambda x: x['score'], reverse=True)
        
        # Return the original report dictionaries in ranked order
        return [item['report'] for item in sorted_reports]
