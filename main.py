import re
import pdfplumber
import fitz
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter

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
        doc = fitz.open(self.pdf_path)
        for page in doc:
            text = page.get_text()
            if text:
                all_text += text.replace("fgos.ru", "").replace(str(self.date), "") + "\n"


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
        doc = fitz.open(self.pdf_path)
        for page in doc:
            text = page.get_text()
            if text:
                all_text += text.replace("fgos.ru", "").replace(str(self.date), "") + "\n"

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
        pattern1 = r'Структура и объем программы \w+'
        pattern2 = r'2\.2\. Программа'

        all_tables = []
        capturing = False

        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                text = text.replace("fgos.ru", "").replace(str(self.date), "").strip()
                if not text:
                    continue

                if re.search(pattern1, text):
                    capturing = True

                if capturing:
                    tables = page.find_tables()
                    for table in tables:
                        table_data = table.extract()
                        if table_data:
                            all_tables.extend(table_data)

                if re.search(pattern2, text):
                    break


        return all_tables

    def extract_praktika(self):
        all_text = ""
        doc = fitz.open(self.pdf_path)
        for page in doc:
            text = page.get_text()
            if text:
                all_text += text.replace("fgos.ru", "").replace(str(self.date), "") + "\n"

        pattern1 = r'Типы учебной практики:'
        pattern2 = r'Типы производственной практики:'
        pattern3 = r'Преддипломная практика проводится для выполнения выпускной квалификационной работы и является обязательной.'

        match1 = re.search(pattern1, all_text)
        match2 = re.search(pattern2, all_text)
        match3 = re.search(pattern3, all_text)

        uch_praktika = []
        pr_praktika = []

        if match1 and match2:
            start_pos = match1.end()
            end_pos = match2.start()
            uch_praktika_text = all_text[start_pos:end_pos].strip()

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
            pr_praktika_text = all_text[start_pos:end_pos].strip()

            sentences = pr_praktika_text.split(';')
            clean_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    if sentence.endswith('.'):
                        sentence = sentence[:-1]
                    clean_sentences.append(sentence)

            pr_praktika = clean_sentences

        doc.close()
        return uch_praktika, pr_praktika

    def extract_uk(self):
        pattern1 = r'3\.2\.\s*Программа[\w\s]+универсальные компетенции:'
        pattern2 = r'3\.3\.\s*Программа\s+\w+'

        doc = fitz.open(self.pdf_path)
        complete_table = []
        capturing = False

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            text = text.replace("fgos.ru", "").replace(str(self.date), "") + "\n"

            if re.search(pattern1, text):
                capturing = True

            if capturing:
                tables = page.find_tables()
                for table in tables:
                    table_data = table.extract()
                    if table_data:
                        for row in table_data:
                            if any(cell for cell in row):
                                clean_row = []
                                for cell in row:
                                    if cell:
                                        cell_clean = re.sub(r'\s+', ' ', str(cell)).strip()
                                        cell_clean = cell_clean.replace("\n", " ").strip()
                                        clean_row.append(cell_clean)
                                    else:
                                        clean_row.append('')
                                complete_table.append(clean_row)

            if re.search(pattern2, text):
                break

        doc.close()

        for i in range(len(complete_table)):
            if complete_table[i][0] == "" and i > 0:
                complete_table[i][0] = complete_table[i - 1][0]

        return complete_table


    def extract_opk(self):
        all_text = ""
        doc = fitz.open(self.pdf_path)
        for page in doc:
            text = page.get_text()
            if text:
                all_text += text.replace("fgos.ru", "").replace(str(self.date), "") + "\n"

        pattern1 = r'3\.3\. Программа [\w\s]+:'
        pattern2 = r'3\.4\. Профессиональные компетенции'

        match1 = re.search(pattern1, all_text)
        match2 = re.search(pattern2, all_text)

        if match1 and match2:
            start_pos = match1.end()
            end_pos = match2.start()
            opk_text = all_text[start_pos:end_pos].strip()

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
            doc.close()
            return processed_opk

    def extract_standard(self):
        pattern1 = r'ПЕРЕЧЕНЬ\s+ПРОФЕССИОНАЛЬНЫХ\s+СТАНДАРТОВ'

        doc = fitz.open(self.pdf_path)
        complete_table = []
        capturing = False

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            text = text.replace("fgos.ru", "").replace(str(self.date), "") + "\n"

            if re.search(pattern1, text):
                capturing = True

            if capturing:
                tables = page.find_tables()
                for table in tables:
                    table_data = table.extract()
                    if table_data:
                        for row in table_data:
                            if any(cell for cell in row):
                                clean_row = []
                                for cell in row:
                                    if cell:
                                        cell_clean = re.sub(r'\s+', ' ', str(cell)).strip()
                                        cell_clean = cell_clean.replace("\n", " ").strip()
                                        clean_row.append(cell_clean)
                                    else:
                                        clean_row.append('')
                                complete_table.append(clean_row)

            if page_num == len(doc) - 1:
                break

        doc.close()
        s=[]
        for i in range(len(complete_table)):
            if complete_table[i][0] == "" and complete_table[i][1] == "":
                complete_table[i-1][2] += complete_table[i][2]
                s.append(i)

        for i in s[::-1]:
            complete_table.pop(i)
        return complete_table

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
                df_specializacii = pd.DataFrame({
                    'Номер специализации': numbers_s,
                    'Название специализации': names_s
                })
                df_specializacii.to_excel(writer, sheet_name='Специализации', index=False)

            # 3. Структура и объем
            structure = self.extract_structure_and_volume()
            if structure:
                if len(structure) > 0:
                    headers = structure[0]
                    data = structure[1:]
                    df_structure = pd.DataFrame(data, columns=headers)
                else:
                    max_cols = max(len(row) for row in structure) if structure else 0
                    df_structure = pd.DataFrame(structure, columns=[f'Колонка_{i + 1}' for i in range(max_cols)])
                df_structure.to_excel(writer, sheet_name='Структура_и_объем', index=False)

            # 4. Практика - объединенная таблица
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
            uk = self.extract_uk()
            if uk:
                if len(uk) > 0:
                    headers = uk[0]
                    data = uk[1:]
                    df_uk = pd.DataFrame(data, columns=headers)
                else:
                    max_cols_uk = max(len(row) for row in uk) if uk else 0
                    df_uk = pd.DataFrame(uk, columns=[f'Колонка_{i + 1}' for i in range(max_cols_uk)])
                df_uk.to_excel(writer, sheet_name='Универсальные_компетенции', index=False)

            # 6. ОПК
            opk = self.extract_opk()
            if opk:
                df_opk = pd.DataFrame(opk, columns=['Код', 'Описание'])
                df_opk.to_excel(writer, sheet_name='ОПК', index=False)

            # 7. Профессиональные стандарты
            standards = self.extract_standard()
            if standards:
                if len(standards) > 0:
                    headers = standards[0]
                    data = standards[1:]
                    df_standards = pd.DataFrame(data, columns=headers)
                else:
                    max_cols_std = max(len(row) for row in standards) if standards else 0
                    df_standards = pd.DataFrame(standards, columns=[f'Колонка_{i + 1}' for i in range(max_cols_std)])
                df_standards.to_excel(writer, sheet_name='Проф_стандарты', index=False)


        workbook = load_workbook(filename)

        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]
            self._auto_adjust_columns(worksheet)

        workbook.save(filename)

        print(f"Все данные сохранены в файл: {filename}")
        return filename


if __name__ == "__main__":
    parser = Parser("112.pdf")

    filename = parser.save_all_to_excel()

    print(f"Файл создан: {filename}")
