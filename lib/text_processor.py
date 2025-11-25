import flitz
from docx import Document

class Textprocessor:
    def __init__(self,logger):
        self.logger=logger
    
    def extract_text_from_pdf(self,pdf_path):
        doc=flitz.open(pdf_path)
        text='\n'.join([page.get_text('text') for page in doc])
        doc.close()
        return text
    
    def extract_text_from_docx(self,docx_path):
        doc=Document(docx_path)
        text='\n'.join([para.text for para in doc.paragraphs])
        return text
    
    def extract_text(self,file_path,file_extension):
        if file_extension=='pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension=='docx':
            return self.extract_text_from_docx(file_path)
        else:
            return ""
        