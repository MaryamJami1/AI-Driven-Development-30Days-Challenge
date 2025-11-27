"""PDF text extraction utility using PyMuPDF."""

import fitz  # PyMuPDF
from typing import Dict, Any


class PDFExtractor:
    """Utility class for extracting text from PDF files."""

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
    MAX_PAGES = 50
    MIN_WORD_COUNT = 100

    @staticmethod
    def validate_pdf(file_data: bytes, file_name: str) -> Dict[str, Any]:
        """
        Validate PDF file before processing.

        Args:
            file_data: The PDF file bytes
            file_name: Name of the file

        Returns:
            Dict with 'valid' (bool) and 'error' (str) keys
        """
        # Check file extension
        if not file_name.lower().endswith('.pdf'):
            return {'valid': False, 'error': 'Invalid file type. Please upload a PDF file.'}

        # Check file size
        if len(file_data) > PDFExtractor.MAX_FILE_SIZE:
            return {
                'valid': False,
                'error': f'File size exceeds {PDFExtractor.MAX_FILE_SIZE // (1024*1024)}MB limit.'
            }

        return {'valid': True, 'error': None}

    @staticmethod
    def extract_text(file_data: bytes) -> Dict[str, Any]:
        """
        Extract text from PDF file.

        Args:
            file_data: The PDF file bytes

        Returns:
            Dict with:
                - success (bool): Whether extraction was successful
                - text (str): Extracted text
                - page_count (int): Number of pages
                - word_count (int): Number of words
                - error (str): Error message if any
        """
        try:
            # Open PDF from bytes
            pdf_document = fitz.open(stream=file_data, filetype="pdf")

            # Check if PDF is encrypted/password-protected
            if pdf_document.is_encrypted:
                pdf_document.close()
                return {
                    'success': False,
                    'text': '',
                    'page_count': 0,
                    'word_count': 0,
                    'error': 'PDF is password-protected. Please unlock the file and try again.'
                }

            page_count = len(pdf_document)

            # Warn about large PDFs
            if page_count > PDFExtractor.MAX_PAGES:
                # Still process but warn
                pass

            # Extract text from all pages
            extracted_text = ""
            for page_num in range(min(page_count, PDFExtractor.MAX_PAGES)):
                page = pdf_document[page_num]
                extracted_text += page.get_text()

            pdf_document.close()

            # Check if text was extracted
            if not extracted_text.strip():
                return {
                    'success': False,
                    'text': '',
                    'page_count': page_count,
                    'word_count': 0,
                    'error': 'No text found in PDF. This may be a scanned document or image-only PDF. OCR is not currently supported.'
                }

            # Count words
            word_count = len(extracted_text.split())

            # Check minimum word count
            if word_count < PDFExtractor.MIN_WORD_COUNT:
                return {
                    'success': False,
                    'text': extracted_text,
                    'page_count': page_count,
                    'word_count': word_count,
                    'error': f'Insufficient content. PDF must contain at least {PDFExtractor.MIN_WORD_COUNT} words. Found {word_count} words.'
                }

            return {
                'success': True,
                'text': extracted_text,
                'page_count': page_count,
                'word_count': word_count,
                'error': None,
                'warning': f'Processing first {PDFExtractor.MAX_PAGES} pages only.' if page_count > PDFExtractor.MAX_PAGES else None
            }

        except Exception as e:
            return {
                'success': False,
                'text': '',
                'page_count': 0,
                'word_count': 0,
                'error': f'Failed to extract text from PDF: {str(e)}'
            }

    @staticmethod
    def truncate_text(text: str, max_tokens: int = 50000) -> Dict[str, Any]:
        """
        Truncate text if it exceeds token limits.

        Args:
            text: The text to truncate
            max_tokens: Maximum number of tokens (approximated as words * 1.3)

        Returns:
            Dict with 'text' (str) and 'truncated' (bool)
        """
        # Rough approximation: 1 token ≈ 0.75 words, so max_words = max_tokens * 0.75
        max_words = int(max_tokens * 0.75)
        words = text.split()

        if len(words) <= max_words:
            return {'text': text, 'truncated': False}

        # Take first 60% and last 40% to preserve context
        first_part_words = int(max_words * 0.6)
        last_part_words = int(max_words * 0.4)

        truncated_text = (
            ' '.join(words[:first_part_words]) +
            '\n\n[... content truncated ...]\n\n' +
            ' '.join(words[-last_part_words:])
        )

        return {'text': truncated_text, 'truncated': True}
