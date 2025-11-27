import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment


class Parser:
    def __init__(self, url):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.url = url
        self.html_content = self.get_page(url)
        self.soup = BeautifulSoup(self.html_content, 'html.parser') if self.html_content else None


        self.date = self.extract_date()

        self.text = self.soup.get_text().replace("fgos.ru", "").replace(str(self.date), "") if self.soup else ""

    def get_page(self, url):
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Ошибка при получении страницы: {e}")
            return None

    def extract_date(self):
        date_pattern = r'\d{1,2}\.\d{1,2}\.\d{4}'
        text = self.soup.get_text()

        date_match = re.search(date_pattern, text)
        if date_match:
            return date_match[0]


    def extract_doc_name(self):
        code_pattern = r'\d{2}\.[0][345]\.\d{2}'
        date_pattern = r'от\s*\d{1,2}\s+\w+\s+\d{4}\s*г\.'

        found_code = None
        found_date = None

        code_match = re.search(code_pattern, self.text)
        if code_match and not found_code:
            found_code = code_match.group()

        date_match = re.search(date_pattern, self.text)
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

        pattern1 = r'2\.2\.[\s\w]+\s\(\w+\)\sпо'
        pattern2 = r'\w\s\w+\s\w+\s\w+\s\"\w+\s\(\w+\)\"'

        match1 = re.search(pattern1, self.text)
        match2 = re.search(pattern2, self.text)

        if match1 and match2:
            start_pos = match1.end()
            end_pos = match2.start()
            disciplines_text = self.text[start_pos:end_pos].strip()
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

        pattern1 = r'1.14. [\w\s]+:'
        pattern2 = r'Программы[\w\s№\",-\[\]]+.'

        match1 = re.search(pattern1, self.text)
        match2 = re.search(pattern2, self.text)

        if match1 and match2:
            start_pos = match1.end()
            end_pos = match2.start()
            specializacii_text = self.text[start_pos:end_pos].strip()
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

    # def extract_structure_and_volume(self):
    #     pattern1 = r'Структура и объем программы \w+'
    #     pattern2 = r'2\.2\. Программа'
    #
    #     all_tables = []
    #     capturing = False
    #
    #     with pdfplumber.open(self.pdf_path) as pdf:
    #         for page_num, page in enumerate(pdf.pages):
    #             text = page.extract_text()
    #             text = text.replace("fgos.ru", "").replace(str(self.date), "").strip()
    #             if not text:
    #                 continue
    #
    #             if re.search(pattern1, text):
    #                 capturing = True
    #
    #             if capturing:
    #                 tables = page.find_tables()
    #                 for table in tables:
    #                     table_data = table.extract()
    #                     if table_data:
    #                         all_tables.extend(table_data)
    #
    #             if re.search(pattern2, text):
    #                 break
    #
    #
    #     return all_tables

    def extract_praktika(self):


        pattern1 = r'Типы учебной практики:'
        pattern2 = r'Типы производственной практики:'
        pattern3 = r'Преддипломная практика проводится для выполнения выпускной квалификационной работы и является обязательной.'

        match1 = re.search(pattern1, self.text)
        match2 = re.search(pattern2, self.text)
        match3 = re.search(pattern3, self.text)

        uch_praktika = []
        pr_praktika = []

        if match1 and match2:
            start_pos = match1.end()
            end_pos = match2.start()
            uch_praktika_text = self.text[start_pos:end_pos].strip()

            sentences = uch_praktika_text.split(';')
            clean_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    if sentence.endswith('.'):
                        sentence = sentence[:-1]
                    clean_sentences.append(sentence)

            uch_praktika = clean_sentences

        if match2 and match3:
            start_pos = match2.end()
            end_pos = match3.start()
            pr_praktika_text = self.text[start_pos:end_pos].strip()

            sentences = pr_praktika_text.split(';')
            clean_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    if sentence.endswith('.'):
                        sentence = sentence[:-1]
                    clean_sentences.append(sentence)

            pr_praktika = clean_sentences

        return uch_praktika, pr_praktika

    # def extract_uk(self):
    #     pattern1 = r'3\.2\.\s*Программа[\w\s]+универсальные компетенции:'
    #     pattern2 = r'3\.3\.\s*Программа\s+\w+'
    #
    #     doc = fitz.open(self.pdf_path)
    #     complete_table = []
    #     capturing = False
    #
    #     for page_num in range(len(doc)):
    #         page = doc[page_num]
    #         text = page.get_text()
    #         text = text.replace("fgos.ru", "").replace(str(self.date), "") + "\n"
    #
    #         if re.search(pattern1, text):
    #             capturing = True
    #
    #         if capturing:
    #             tables = page.find_tables()
    #             for table in tables:
    #                 table_data = table.extract()
    #                 if table_data:
    #                     for row in table_data:
    #                         if any(cell for cell in row):
    #                             clean_row = []
    #                             for cell in row:
    #                                 if cell:
    #                                     cell_clean = re.sub(r'\s+', ' ', str(cell)).strip()
    #                                     cell_clean = cell_clean.replace("\n", " ").strip()
    #                                     clean_row.append(cell_clean)
    #                                 else:
    #                                     clean_row.append('')
    #                             complete_table.append(clean_row)
    #
    #         if re.search(pattern2, text):
    #             break
    #
    #     doc.close()
    #
    #     for i in range(len(complete_table)):
    #         if complete_table[i][0] == "" and i > 0:
    #             complete_table[i][0] = complete_table[i - 1][0]
    #
    #     return complete_table


    def extract_opk(self):

        pattern1 = r'3\.3\. Программа [\w\s]+:'
        pattern2 = r'3\.4\. Профессиональные компетенции'

        match1 = re.search(pattern1, self.text)
        match2 = re.search(pattern2, self.text)

        if match1 and match2:
            start_pos = match1.end()
            end_pos = match2.start()
            opk_text = self.text[start_pos:end_pos].strip()

            opk_items = []
            i = 0
            while i < len(opk_text):
                if (i <= len(opk_text) - 3 and
                        opk_text[i] == "О" and
                        opk_text[i + 1] == "П" and
                        opk_text[i + 2] == "К"):

                    next_opk = opk_text.find("ОПК", i + 3)
                    if next_opk == -1:
                        next_opk = len(opk_text)

                    opk_item = opk_text[i:next_opk].strip()
                    semicolon_pos = opk_item.find(';')
                    if semicolon_pos != -1:
                        opk_item = opk_item[:semicolon_pos]

                    opk_items.append(opk_item)
                    i = next_opk
                else:
                    i += 1

            processed_opk = []

            for opk in opk_items:
                if opk:
                    parts = opk.split('.', 1)
                    if len(parts) == 2:
                        code = parts[0].strip()
                        description = parts[1].strip().replace("\n", " ").replace(';', '')

                        if re.match(r'^\d+\.', description):
                            digit_match = re.match(r'^(\d+)\.\s*(.+)', description)
                            if digit_match:
                                digit = digit_match.group(1)
                                clean_description = digit_match.group(2)
                                new_code = f"{code}.{digit}"
                                processed_opk.append([new_code, clean_description])
                            else:
                                processed_opk.append([code, description])
                        else:
                            processed_opk.append([code, description])

            for opk in processed_opk:
                if "." in opk[1]:
                    dot_index = opk[1].find(".")
                    if dot_index != -1:
                        opk[1] = opk[1][:dot_index]

            def opk_key(item):
                code = item[0]
                numbers = re.findall(r'\d+', code)
                return tuple(map(int, numbers))

            processed_opk.sort(key=opk_key)
            return processed_opk

    # def extract_standard(self):
    #     pattern1 = r'ПЕРЕЧЕНЬ\s+ПРОФЕССИОНАЛЬНЫХ\s+СТАНДАРТОВ'
    #
    #     doc = fitz.open(self.pdf_path)
    #     complete_table = []
    #     capturing = False
    #
    #     for page_num in range(len(doc)):
    #         page = doc[page_num]
    #         text = page.get_text()
    #         text = text.replace("fgos.ru", "").replace(str(self.date), "") + "\n"
    #
    #         if re.search(pattern1, text):
    #             capturing = True
    #
    #         if capturing:
    #             tables = page.find_tables()
    #             for table in tables:
    #                 table_data = table.extract()
    #                 if table_data:
    #                     for row in table_data:
    #                         if any(cell for cell in row):
    #                             clean_row = []
    #                             for cell in row:
    #                                 if cell:
    #                                     cell_clean = re.sub(r'\s+', ' ', str(cell)).strip()
    #                                     cell_clean = cell_clean.replace("\n", " ").strip()
    #                                     clean_row.append(cell_clean)
    #                                 else:
    #                                     clean_row.append('')
    #                             complete_table.append(clean_row)
    #
    #         if page_num == len(doc) - 1:
    #             break
    #
    #     doc.close()
    #     s=[]
    #     for i in range(len(complete_table)):
    #         if complete_table[i][0] == "" and complete_table[i][1] == "":
    #             complete_table[i-1][2] += complete_table[i][2]
    #             s.append(i)
    #
    #     for i in s[::-1]:
    #         complete_table.pop(i)
    #     return complete_table

    def _auto_adjust_columns(self, worksheet):
        for column in worksheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)

            for cell in column:
                cell.alignment = Alignment(wrap_text=True, vertical='top')

                if cell.value:
                    lines = str(cell.value).split('\n')
                    max_line_length = max(len(line) for line in lines) if lines else 0
                    max_length = max(max_length, max_line_length)

            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    def save_all_to_excel(self, filename=None):
        if filename is None:
            doc_name = self.extract_doc_name()
            filename = f"{doc_name}.xlsx"
        elif not filename.endswith('.xlsx'):
            filename += '.xlsx'

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:

            # 1. Дисциплины специальности
            discipliny = self.extract_discipliny_specialiteta()
            if discipliny:
                df_discipliny = pd.DataFrame(discipliny, columns=['Дисциплины'])
                df_discipliny.to_excel(writer, sheet_name='Дисциплины', index=False)

            # 2. Специализации
            specializacii = self.extract_specializacii()
            if specializacii and len(specializacii) == 2:
                numbers_s, names_s = specializacii
                max_len = max(len(numbers_s), len(names_s))

                numbers_s_extended = numbers_s + [''] * (max_len - len(numbers_s))
                names_s_extended = names_s + [''] * (max_len - len(names_s))

                df_specializacii = pd.DataFrame({
                    'Номер специализации': numbers_s_extended,
                    'Название специализации': names_s_extended
                })
                df_specializacii.to_excel(writer, sheet_name='Специализации', index=False)

            # 3. Структура и объем
            # structure = self.extract_structure_and_volume()
            # if structure:
            #     max_cols = max(len(row) for row in structure) if structure else 0
            #     df_structure = pd.DataFrame(structure, columns=[f'Колонка_{i + 1}' for i in range(max_cols)])
            #     df_structure.to_excel(writer, sheet_name='Структура_и_объем', index=False)

            # 4. Практика
            praktika = self.extract_praktika()
            if praktika and len(praktika) == 2:
                uch_praktika, pr_praktika = praktika
                max_len = max(len(uch_praktika), len(pr_praktika))

                uch_praktika_extended = uch_praktika + [''] * (max_len - len(uch_praktika))
                pr_praktika_extended = pr_praktika + [''] * (max_len - len(pr_praktika))

                df_praktika = pd.DataFrame({
                    'Учебная практика': uch_praktika_extended,
                    'Производственная практика': pr_praktika_extended
                })
                df_praktika.to_excel(writer, sheet_name='Практика', index=False)

            # 5. Универсальные компетенции
            # uk = self.extract_uk()
            # if uk:
            #     if len(uk) > 0 and isinstance(uk[0], list):
            #         df_uk = pd.DataFrame(uk, columns=['Код', 'Описание'])
            #     else:
            #         df_uk = pd.DataFrame(uk, columns=['Универсальные компетенции'])
            #     df_uk.to_excel(writer, sheet_name='Универсальные_компетенции', index=False)

            # 6. ОПК
            opk = self.extract_opk()
            if opk:
                if len(opk) > 0 and isinstance(opk[0], list):
                    df_opk = pd.DataFrame(opk, columns=['Код', 'Описание'])
                else:
                    df_opk = pd.DataFrame(opk, columns=['ОПК'])
                df_opk.to_excel(writer, sheet_name='ОПК', index=False)

            # 7. Профессиональные стандарты
            # standards = self.extract_standard()
            # if standards:
            #     df_standards = pd.DataFrame(standards, columns=['Профессиональные стандарты'])
            #     df_standards.to_excel(writer, sheet_name='Проф_стандарты', index=False)


        workbook = load_workbook(filename)
        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]
            self._auto_adjust_columns(worksheet)

        workbook.save(filename)
        return filename


if __name__ == "__main__":
    url = "https://fgos.ru/fgos/fgos-10-05-03-informacionnaya-bezopasnost-avtomatizirovannyh-sistem-1457/"

    parser = Parser(url)

    if parser.soup:
        excel_file = parser.save_all_to_excel()


