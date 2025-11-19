import re
import pdfplumber


class Parser:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.date = self.extract_date()

    def extract_date(self):
        date = ''
        all_text = ""
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"

        lines = [line.strip() for line in all_text.split('\n') if line.strip()]

        date_pattern = r'\d{1,2}\.\d{1,2}\.\d{4}'

        for line in lines:
            date_match = re.search(date_pattern, line)
            if date_match:
                date = date_match.group()
                break

        return date


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
                text = page.extract_text().replace("fgos.ru","").replace("self.date", "")
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
                text = page.extract_text().replace("fgos.ru","").replace("self.date", "")
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





    def extract_structure_and_volume(self):
        pattern1 = r'Структура и объем программы \w+\nТаблица\n'
        pattern2 = r'2\.2\. Программа'

        table = None
        first_page = None
        found_first_pattern = False


        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text().replace("fgos.ru","").replace("self.date", "")
                if not text:
                    continue

                if re.search(pattern1, text):
                    found_first_pattern = True
                    first_page = page
                    continue

                if found_first_pattern and re.search(pattern2, text):
                    if first_page:

                        table1 = first_page.extract_table()
                        table2 = page.extract_table()

                        if table1 and table2:
                            table = table1 + table2

                        elif table1:
                            table = table1

                        elif table2:
                            table = table2

                    else:
                        table = page.extract_table()
                    break
                if found_first_pattern and page_num == len(pdf.pages) - 1:
                    table = first_page.extract_table() if first_page else None

        return table







    def extract_praktika(self):
        all_text = ""
        uch_praktika=None
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"

        pattern1 = r'Типы учебной практики:'
        pattern2 = r'Типы производственной практики:'
        pattern3 = r'Преддипломная практика проводится для выполнения выпускной квалификационной работы и является обязательной.'

        match1 = re.search(pattern1, all_text)
        match2 = re.search(pattern2, all_text)
        match3 = re.search(pattern3, all_text)

        if match1 and match2:
            start_pos = match1.end()
            end_pos = match2.start()
            uch_praktika_text = all_text[start_pos:end_pos].strip().replace("fgos.ru","").replace("self.date", "")
            uch_praktika = [uch_praktika.strip().replace(".","") for uch_praktika in uch_praktika_text.split(';')]
            uch_praktika.insert(0,'Типы учебной практики:')

        if match2 and match3:
            start_pos = match2.end()
            end_pos = match3.start()
            pr_praktika_text = all_text[start_pos:end_pos].strip().replace("fgos.ru","").replace("self.date", "")
            pr_praktika = [pr_praktika.strip().replace(".","") for pr_praktika in pr_praktika_text.split(';')]
            pr_praktika.insert(0,'Типы производственной практики:')

        return uch_praktika, pr_praktika






    # def extract_uk(self):
    #     pattern1 = r'"3.2. Программа \w+ должна устанавливать следующие универсальные компетенции:'
    #     pattern2 = r'3\.3\. Программа \w+'
    #
    #     table = None
    #     page1 = None
    #     found_first_pattern = False
    #
    #
    #     with pdfplumber.open(self.pdf_path) as pdf:
    #         for page in pdf.pages:
    #             text = page.extract_text()
    #             if not text:
    #                 continue
    #             if re.search(pattern1, text):
    #                 found_first_pattern = True
    #                 page1 = page
    #                 continue
    #             if found_first_pattern and re.search(pattern2, text):
    #                 if page1:
    #                     table1 = page1.extract_table()
    #                     table2 = page.extract_table()
    #                     if table1 and table2:
    #                         table = table1 + table2
    #                     elif table1:
    #                         table = table1
    #                     elif table2:
    #                         table = table2
    #                 else:
    #                     table = page.extract_table()
    #                 break
    #
    #
    #             if found_first_pattern and not re.search(pattern2, text):
    #                 table = page1.extract_table() if page1 else page.extract_table()
    #
    #     return table


    """
    def extract_opk(self):
        all_text = ""
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"

        pattern1 = r'3\.3\. Программа [\w\s]+:'
        pattern2 = r'3.4. Профессиональные компетенции'

        match1 = re.search(pattern1, all_text)
        match2 = re.search(pattern2, all_text)

        if match1 and match2:
            start_pos = match1.end()
            end_pos = match2.start()
            opk_text = all_text[start_pos:end_pos].strip().replace("fgos.ru","").replace()
            opk = [opk.strip() for opk in opk_text.split(';')]

            num1 = []
            for i in range(len(spezializacii)):
                if spezializacii[i] == '':
                    num1.append(i)
                if ";" in spezializacii[i]:
                    num2 = 0
                    for j in range(len(spezializacii[i])):
                        if spezializacii[i][j] == ";":
                            num2 = j
                    spezializacii[i] = spezializacii[i][:num2]

            for i in num1[::-1]:
                spezializacii.pop(i)
            numbers_s = []
            names_s = []

            for i in range(len(spezializacii)):
                for j in range(len(spezializacii[i])):
                    if spezializacii[i][j] == '"':
                        numbers_s.append((spezializacii[i][:j]).strip(" "))
                        names_s.append((spezializacii[i][j:]).strip(" "))
                        break
            names_s_s = []
            for name in names_s:
                names_s_s.append(name.replace("\n", " ").replace('"', ""))

            return numbers_s, names_s_s
    """


    def close(self):
        pass



if __name__ == "__main__":
    parser = Parser("123.pdf")
    doc_name = parser.extract_doc_name()
    discipliny_specialiteta = parser.extract_discipliny_specialiteta()
    specializacii_specialiteta = parser.extract_specializacii()
    structure_and_vloume = parser.extract_structure_and_volume()
    praktika = parser.extract_praktika()
    #u_kompetencii = parser.extract_uk()
    print(doc_name)
    print(discipliny_specialiteta)
    print(specializacii_specialiteta)
    print(structure_and_vloume)
    print(praktika)
    print(parser.date)
    #print(u_kompetencii)
    parser.close()