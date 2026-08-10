from unittest.mock import MagicMock, patch
import pytest
from app.utils.document_parsers import parse_pdf, parse_docx, extract_text_from_file
from app.core.exceptions import DocumentParsingException

def test_parse_pdf_success():
    with patch("fitz.open") as mock_open:
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "John Doe\nSkills: Python, FastAPI"
        mock_doc.__iter__.return_value = [mock_page]
        mock_open.return_value = mock_doc
        
        text = parse_pdf(b"fake pdf content")
        assert "John Doe" in text
        assert "FastAPI" in text
        mock_doc.close.assert_called_once()

def test_parse_pdf_empty():
    with patch("fitz.open") as mock_open:
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = ""
        mock_doc.__iter__.return_value = [mock_page]
        mock_open.return_value = mock_doc
        
        with pytest.raises(DocumentParsingException) as exc_info:
            parse_pdf(b"empty pdf")
        assert "PDF is empty" in str(exc_info.value)

def test_parse_docx_success():
    with patch("docx.Document") as mock_doc_class:
        mock_doc = MagicMock()
        mock_para = MagicMock()
        mock_para.text = "Jane Doe\nSkills: Go, AWS"
        mock_doc.paragraphs = [mock_para]
        
        # Mock tables
        mock_table = MagicMock()
        mock_row = MagicMock()
        mock_cell = MagicMock()
        mock_cell.text = "Certification: AWS Architect"
        mock_row.cells = [mock_cell]
        mock_table.rows = [mock_row]
        mock_doc.tables = [mock_table]
        
        mock_doc_class.return_value = mock_doc
        
        text = parse_docx(b"fake docx content")
        assert "Jane Doe" in text
        assert "AWS Architect" in text

def test_extract_text_from_file_unsupported():
    with pytest.raises(DocumentParsingException) as exc_info:
        extract_text_from_file("resume.txt", b"txt content")
    assert "Unsupported file format" in str(exc_info.value)
