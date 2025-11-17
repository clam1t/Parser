import re
import pdfplumber


class Parser:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_doc_name(self):
        doc_name = ''
        all_text = ""


        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"

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


        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"


        pattern1 = r'2\.2\.[\s\w]+\s\(\w+\)\sпо'
        pattern2 = r'\w\s\w+\s\w+\s\w+\s\"\w+\s\(\w+\)\"'

        match1 = re.search(pattern1, all_text)
        match2 = re.search(pattern2, all_text)

        if match1 and match2:
            start_pos = match1.end()
            end_pos = match2.start()
            disciplines_text = all_text[start_pos:end_pos].strip()
            disciplines = [discipline.strip() for discipline in disciplines_text.split(',')]

            all_disciplines = []
            i = 0
            while i < len(disciplines) - 1:
                if "(" in disciplines[i] and ")" not in disciplines[i]:
                    disciplines[i] = str(disciplines[i]) + " " + str(disciplines[i + 1])
                    disciplines.pop(i + 1)
                else:
                    i += 1
            list_disciplin = []
            for discipline in disciplines:
                list_disciplin. append(discipline.replace("\n"," "))

            for discipline in list_disciplin:
                print(discipline)
                match = re.search(r'\((.*?)\)', discipline)
                if not match:
                    all_disciplines.append(discipline)
                if match:
                    content = match.group(1)
                    print(content)
                    letter_content=[]

                    for letter in content:
                        letter_content.append(letter)
                    pos_s=[-1]
                    for i in range(len(letter_content)):
                        if re.search(r'\s', letter_content[i]):
                            pos_s.append(i)
                    pos_s.append(len(letter_content))
                    print(pos_s)
                    itog_content=[]
                    for i in range(len(pos_s)-1):
                        itog_content.append(letter_content[pos_s[i]+1:pos_s[i+1]])
                    print(itog_content)
                    itog_slova=[]
                    for i in range(len(itog_content)):
                        slovo = ''
                        for j in range(len(itog_content[i])):
                            slovo+=itog_content[i][j]
                        itog_slova.append(slovo)
                    print(itog_slova)
                    super_itog_slova=[]
                    unique_words = list(dict.fromkeys(itog_slova))

                    if unique_words:
                        base_word = unique_words[0]
                        for word in unique_words[1:]:
                            super_itog_slova.append(f"{base_word} {word}")

                    print(super_itog_slova)
                    all_disciplines.extend(super_itog_slova)


            return all_disciplines

        return []

    def close(self):
        pass



if __name__ == "__main__":
    parser = Parser("123.pdf")
    doc_name = parser.extract_doc_name()
    discipliny_specialiteta = parser.extract_discipliny_specialiteta()
    print("Название документа:", doc_name)
    print("Дисциплины специальности:", discipliny_specialiteta)
    parser.close()