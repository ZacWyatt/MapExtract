import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from PyPDF2 import PdfMerger

class WebsiteToPDF:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.output_dir = Path('pdf_output') / self.domain
        self.processed_urls = set()
        self.generated_pdfs = []  # List to store generated PDF paths in order
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_sitemap_url(self):
        """Try to find the sitemap URL from robots.txt or common locations."""
        # Common sitemap locations
        common_sitemap_paths = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap/sitemap.xml'
        ]
        
        # Try robots.txt first
        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            response = requests.get(robots_url)
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if 'sitemap:' in line.lower():
                        return line.split(':', 1)[1].strip()
        except:
            pass

        # Try common sitemap locations
        for path in common_sitemap_paths:
            sitemap_url = urljoin(self.base_url, path)
            try:
                response = requests.get(sitemap_url)
                if response.status_code == 200:
                    return sitemap_url
            except:
                continue

        return None

    def parse_sitemap(self, sitemap_url):
        """Parse the sitemap XML and extract URLs."""
        try:
            response = requests.get(sitemap_url)
            if response.status_code != 200:
                print(f"Failed to fetch sitemap: {sitemap_url}")
                return []

            soup = BeautifulSoup(response.content, 'xml')
            urls = []
            
            # Handle both regular sitemaps and sitemap indexes
            if soup.find('sitemapindex'):
                # This is a sitemap index
                for sitemap in soup.find_all('loc'):
                    if 'sitemap' in sitemap.text:
                        urls.extend(self.parse_sitemap(sitemap.text))
            else:
                # This is a regular sitemap
                for url in soup.find_all('loc'):
                    urls.append(url.text)

            return urls
        except Exception as e:
            print(f"Error parsing sitemap: {e}")
            return []

    def url_to_filename(self, url):
        """Convert URL to a valid filename."""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if not path:
            path = 'index'
        # Replace invalid filename characters
        filename = path.replace('/', '_').replace('?', '_').replace('&', '_')
        return f"{filename}.pdf"

    def convert_to_pdf(self, url, browser):
        """Convert a webpage to PDF."""
        if url in self.processed_urls:
            return

        try:
            filename = self.url_to_filename(url)
            output_path = self.output_dir / filename

            # Create a new page
            page = browser.new_page()
            
            # Navigate to the URL
            page.goto(url, wait_until='networkidle')
            
            # Generate PDF
            page.pdf(path=str(output_path), format='A4', margin={
                'top': '0.75in',
                'right': '0.75in',
                'bottom': '0.75in',
                'left': '0.75in'
            })
            
            # Close the page
            page.close()
            
            self.processed_urls.add(url)
            self.generated_pdfs.append(output_path)  # Add to list of generated PDFs
            print(f"Converted: {url} -> {output_path}")
            
            # Be nice to the server
            time.sleep(1)
            
        except Exception as e:
            print(f"Error converting {url} to PDF: {e}")

    def merge_pdfs(self):
        """Merge all generated PDFs into a single file and delete source files."""
        if not self.generated_pdfs:
            print("No PDFs to merge.")
            return

        merger = PdfMerger()
        output_file = Path('pdf_output') / f"{self.domain}_complete.pdf"

        print("\nMerging PDFs...")
        for pdf_path in self.generated_pdfs:
            try:
                merger.append(str(pdf_path))
                print(f"Added: {pdf_path.name}")
            except Exception as e:
                print(f"Error adding {pdf_path.name}: {e}")

        try:
            merger.write(str(output_file))
            merger.close()
            print(f"\nMerged PDF saved as: {output_file}")

            # Delete source files after successful merge
            print("\nCleaning up source files...")
            for pdf_path in self.generated_pdfs:
                try:
                    pdf_path.unlink()
                    print(f"Deleted: {pdf_path.name}")
                except Exception as e:
                    print(f"Error deleting {pdf_path.name}: {e}")

        except Exception as e:
            print(f"Error saving merged PDF: {e}")

        os.rmdir(self.output_dir)

    def process_website(self):
        """Main method to process the website."""
        print(f"Processing website: {self.base_url}")
        
        # Get sitemap URL
        sitemap_url = self.get_sitemap_url()
        if not sitemap_url:
            print("Could not find sitemap. Please provide the sitemap URL manually.")
            return

        print(f"Found sitemap: {sitemap_url}")
        
        # Parse sitemap and get URLs
        urls = self.parse_sitemap(sitemap_url)
        if not urls:
            print("No URLs found in sitemap.")
            return

        print(f"Found {len(urls)} URLs in sitemap.")
        
        # Launch browser and process URLs
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            
            # Convert each URL to PDF
            for i, url in enumerate(urls, 1):
                print(f"Processing {i}/{len(urls)}: {url}")
                self.convert_to_pdf(url, browser)
            
            browser.close()

        # Merge all PDFs
        self.merge_pdfs()

        print(f"\nConversion complete! PDFs saved in: {self.output_dir}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python website_to_pdf.py <website_url>")
        sys.exit(1)

    website_url = sys.argv[1]
    converter = WebsiteToPDF(website_url)
    converter.process_website()

if __name__ == "__main__":
    main() 