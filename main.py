import re
import fitz
import pandas as pd

class Parser:
    def __init__(self, filename):
        self.doc = fitz.open(filename)


    def extract_doc_name(self):
        doc_name = ''
        code_name = r'\d{2}\.\d{2}\.\d{2}'
        date_name = r'\w{от}\ \d{2}\ \w{}\ \d{4}\ \w{г}\.'
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            lines = text.split('\n')
            for line in lines:
                code_match = re.search(code_name, line)
                date_match = re.search(date_name, line)

                if code_match and date_match:
                    doc_name = line.strip()
                    return doc_name
        return doc_name

    def close(self):
        self.doc.close()

parser = Parser("123.pdf")
doc_name = parser.extract_doc_name()
print("Найденное название:", doc_name)
parser.close()


