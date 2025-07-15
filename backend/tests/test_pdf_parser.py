from backend.parsers.pdf_parser import extract_text_from_pdf

def test_pdf():
    print(extract_text_from_pdf("tests/sample.pdf"))
