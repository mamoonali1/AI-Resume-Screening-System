import pdfplumber
import docx
import io

def extract_text_from_file(file_storage) -> str:
    """Extracts raw text from uploaded PDF or DOCX file objects."""
    filename = file_storage.filename.lower()
    file_bytes = file_storage.read()
    text = ""

    if filename.endswith('.pdf'):
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    
    elif filename.endswith('.docx'):
        doc = docx.Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            if para.text:
                text += para.text + "\n"
                
    return text.strip()