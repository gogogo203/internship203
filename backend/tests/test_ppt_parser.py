from backend.parsers.ppt_parser import extract_text_from_pptx

def test_ppt():
    print(extract_text_from_pptx("tests/sample.pptx"))
