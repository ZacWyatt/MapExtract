# Website to PDF Scraper

This application takes a website URL, extracts its sitemap, and converts all pages to a single collated PDF document. It uses Playwright for high-quality PDF generation and handles both regular sitemaps and sitemap indexes.

## Features

- Automatically detects and parses sitemap.xml
- Converts all pages to PDF format
- Collates all PDFs into a single document
- Handles relative and absolute URLs
- Progress tracking during conversion
- Automatic cleanup of temporary files
- Supports JavaScript-rendered content
- High-quality PDF output with proper formatting

## Prerequisites

- Python 3.7+
- Playwright (will be installed automatically)

## Installation

1. Clone or download this repository

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
python -m playwright install
```

## Usage

Run the script with a website URL:
```bash
python website_to_pdf.py https://example.com
```

The script will:
1. Find and parse the website's sitemap
2. Convert each page to PDF
3. Merge all PDFs into a single document
4. Clean up temporary files
5. Save the final PDF as `{domain}_complete.pdf` in the `pdf_output` directory

## Output

The final output will be a single PDF file named `{domain}_complete.pdf` in the `pdf_output` directory. For example:
- Input URL: `https://example.com`
- Output file: `pdf_output/example.com_complete.pdf`

## Error Handling

The script includes comprehensive error handling for:
- Sitemap detection and parsing
- PDF generation
- File merging
- Cleanup operations

If any errors occur during processing, they will be reported in the console output.

## Notes

- The script includes a 1-second delay between page requests to be respectful to servers
- All temporary PDFs are automatically cleaned up after successful merge
- The final PDF maintains the order of pages as they appear in the sitemap
- JavaScript-rendered content is properly captured in the PDFs 