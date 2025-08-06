"""
Enhanced Document Reader with proper encoding detection
"""

import chardet
from pathlib import Path
import PyPDF2
import docx


class EnhancedDocumentReader:
    """Handles multiple document formats with encoding detection"""
    
    @staticmethod
    def read_file(file_path: Path) -> str:
        """Read content from various file formats"""
        extension = file_path.suffix.lower()
        
        if extension == '.txt':
            return EnhancedDocumentReader._read_text_with_encoding(file_path)
        elif extension == '.pdf':
            return EnhancedDocumentReader._read_pdf(file_path)
        elif extension in ['.doc', '.docx']:
            return EnhancedDocumentReader._read_word(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    @staticmethod
    def _read_text_with_encoding(file_path: Path) -> str:
        """Read text file with automatic encoding detection"""
        # First, detect the encoding
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
        
        # Try detected encoding, fallback to common encodings
        encodings_to_try = [encoding, 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for enc in encodings_to_try:
            if enc:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        content = f.read()
                        # Clean up common encoding issues
                        content = content.replace('\u2019', "'")  # Right single quote
                        content = content.replace('\u201c', '"')  # Left double quote
                        content = content.replace('\u201d', '"')  # Right double quote
                        content = content.replace('\u2013', '-')  # En dash
                        content = content.replace('\u2014', '--') # Em dash
                        content = content.replace('\u2026', '...') # Ellipsis
                        return content
                except (UnicodeDecodeError, AttributeError):
                    continue
        
        # If all else fails, read with errors ignored
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    @staticmethod
    def _read_pdf(file_path: Path) -> str:
        """Read PDF file content"""
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        return text
    
    @staticmethod
    def _read_word(file_path: Path) -> str:
        """Read Word document content"""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text