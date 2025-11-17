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
            doc_name = f"{found_code}_{found_date.replace(' ', '_')}"
        elif found_code:
            doc_name = found_code
        elif found_date:
            doc_name = found_date

        return doc_name

    def extract_discipliny_specialiteta(self):
        disciplines = []
        all_text = ""
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            all_text += text

        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        pattern1 = r'2.2.[\s\w]+\s\(\w+\)\sпо'
        pattern2 = r'\w\s\w+\s\w+\s\w+\s\"\w+\s\(\w+\)\"'

        match1 = re.search(pattern1, all_text)
        match2 = re.search(pattern2, all_text)

        if match1 and match2:
            start_pos = match1.end()
            end_pos = match2.start()
            disciplines = all_text[start_pos:end_pos].strip()
            disciplines = [discipline.strip() for discipline in disciplines.split(',')]
            all_disciplines = []
            for i in range (len(disciplines)-1):
                if "(" in disciplines[i]:
                    disciplines[i]= str(disciplines[i])+" "+str(disciplines[i+1])
                    disciplines.pop(i+1)
            for discipline in disciplines:
                match = re.search(r'\((.*?)\)', discipline)
                if match:
                    content = match.group(1)
                    cleaned_content = ' '.join(content.split())
                    all_disciplines.append(cleaned_content)

            return list(dict.fromkeys(all_disciplines))



    def close(self):
        self.doc.close()


parser = Parser("123.pdf")
doc_name = parser.extract_doc_name()
discipliny_specialiteta = parser.extract_discipliny_specialiteta()
print(doc_name)
print(discipliny_specialiteta)
parser.close()