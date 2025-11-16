import re
import fitz


class Parser:
    def __init__(self, pdf_path):
        self.doc = fitz.open(pdf_path)

    def extract_doc_name(self):
        doc_name = ''
        all_text = ""
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            all_text += text


        lines = [line.strip() for line in all_text.split('\n') if line.strip()]

        code_pattern = r'\d{2}\.[0][456]\.\d{2}'
        date_pattern = r'от\s*\d{1,2}\s+\w+\s+\d{4}\s*г\.'

        found_code = None
        found_date = None

        for line in lines:
            code_match = re.search(code_pattern, line)
            if code_match and not found_code:
                found_code = code_match.group()

            date_match = re.search(date_pattern, line)
            if date_match and not found_date:
                found_date = date_match.group()


        if found_code and found_date:
            doc_name = f"{found_code}_{found_date.replace(' ','_')}"
        elif found_code:
            doc_name = found_code
        elif found_date:
            doc_name = found_date

        return doc_name

    def close(self):
        self.doc.close()



parser = Parser("123.pdf")
doc_name = parser.extract_doc_name()
print("Найденное название:", doc_name)
parser.close()