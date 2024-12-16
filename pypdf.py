from PyPDF2 import PdfReader

try:
    reader = PdfReader("/Users/santoshtalluri/Documents/MyDevProjects/rag_with_url_project/data/Santosh.pdf")
    content = ''.join(page.extract_text() for page in reader.pages if page.extract_text())
    print(f"Extracted content from PDF (first 500 chars): {content[:500]}")
except Exception as e:
    print(f'Error reading PDF file: {e}')