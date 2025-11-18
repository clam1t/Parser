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

        code_pattern = r'\d{2}\.[0][345]\.\d{2}'
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
            a=''
            i = 0
            while i < len(disciplines):
                if "(" in disciplines[i]:
                    a=[]
                    n = [i]
                    a.append(disciplines[i])
                    j = i + 1
                    while j < len(disciplines) and ")" not in disciplines[j]:
                        a.append(disciplines[j])
                        n.append(j)
                        j += 1

                    if j < len(disciplines):
                        a.append(disciplines[j])
                        n.append(j)

                    for q in n[::-1]:
                        disciplines.pop(q)

                    for z in range(len(a)):
                        disciplines.insert(n[0]+z, a[z])

                    i = n[0] + 1
                else:
                    i += 1
            for i in range(len(disciplines)):
                if "(" in disciplines[i]:
                    for j in range(len(disciplines[i])):
                        if disciplines[i][j] == "(":
                            a = j + 1
                            break
                    disciplines[i] = str(disciplines[i][a:])

                if ")" in disciplines[i]:
                    for j in range(len(disciplines[i])):
                        if disciplines[i][j] == ")":
                            b = j
                            break
                    disciplines[i] = str(disciplines[i][:b])

            list_disciplin = []
            for discipline in disciplines:
                list_disciplin.append(discipline.replace("\n"," "))
            return list_disciplin

    def extract_specializacii(self):
        all_text = ""
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"

        pattern1 = r'1.14. [\w\s]+:'
        pattern2 = r'Программы[\w\s№\",-\[\]]+.'

        match1 = re.search(pattern1, all_text)
        match2 = re.search(pattern2, all_text)

        if match1 and match2:
            start_pos = match1.end()
            end_pos = match2.start()
            specializacii_text = all_text[start_pos:end_pos].strip()
            spezializacii = [specializacia.strip() for specializacia in specializacii_text.split('специализация №')]

            num1=[]
            for i in range(len(spezializacii)):
                if spezializacii[i]=='':
                    num1.append(i)
                if ";" in spezializacii[i]:
                    num2=0
                    for j in range(len(spezializacii[i])):
                        if spezializacii[i][j]==";":
                            num2=j
                    spezializacii[i]=spezializacii[i][:num2]

            for i in num1[::-1]:
                spezializacii.pop(i)
            numbers_s=[]
            names_s=[]

            for i in range(len(spezializacii)):
                for j in range(len(spezializacii[i])):
                    if spezializacii[i][j]=='"':
                        numbers_s.append((spezializacii[i][:j]).strip(" "))
                        names_s.append((spezializacii[i][j:]).strip(" "))
                        break
            names_s_s=[]
            for name in names_s:
                names_s_s.append(name.replace("\n"," ").replace('"',""))


            return numbers_s, names_s_s

    def close(self):
        pass



if __name__ == "__main__":
    parser = Parser("123.pdf")
    doc_name = parser.extract_doc_name()
    discipliny_specialiteta = parser.extract_discipliny_specialiteta()
    specializacii_specialiteta = parser.extract_specializacii()
    print("Название документа:", doc_name)
    print("Дисциплины специальности:", discipliny_specialiteta)
    print("специализации специальности:", specializacii_specialiteta)
    parser.close()