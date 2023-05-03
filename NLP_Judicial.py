## Libraries Required

import PyPDF2
import re
from num2words import num2words
from fpdf import FPDF
import numpy as np
from dateutil.parser import parse
import pdfplumber
import sys


# Rule 1
def remove_header(page_text):
    """
    Removes all text and spaces from the beginning of the page text
    until the text "Opinion of the Court" is found.

    Args:
        page_text (str): The text of a single page.

    Returns:
    0
        The page text with the header removed.
    """
    # Remove text from the first page until the end of the sentence containing "SUPREME COURT OF THE UNITED STATES"
    if "SUPREME COURT OF THE UNITED STATES" in page_text:
        page_text = re.sub(r'^.*?SUPREME COURT OF THE UNITED STATES', '', page_text, flags=re.DOTALL)

    # Use regular expression to find the header and replace it with an empty string
    cleaned_page_text = re.sub(r"^(.*?)Opinion of the Court", "", page_text, flags=re.DOTALL)
   
    return cleaned_page_text


def remove_pageNumber(page_text):
    new_text_list = []
    for text in page_text:
        new_text = re.sub(r'^\s*\d{1,2}\s*', '', text)
        new_text_list.append(new_text)

    return new_text_list

def remove_footer(page_text):
    new_clean_text = []
    for text in page_text:
        if "——————" in text:
            new_text = text.split("——————")[0]
        else:
            new_text = text
        new_clean_text.append(new_text)
        
    return new_clean_text

# Define a mapping of digits to their spoken form
digit_mapping = {
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine"
}

# Extracting Names
def name_extract(page_text):
    # Search for the desired text
    
    text = page_text[:page_text.find('Opinion of the Court')]
    print(text)
    text = text.replace('v.', 'versus')
    return text


# function to add day suffix
def add_day_suffix(day):
    if 11 <= day <= 13:
        return str(day) + 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return str(day) + suffix

def extract_Decide_date(text):
    date = parse(text, fuzzy=True)

    # extract only the date component
    date_only = date.date()
    
    # format the date with month in words and day with suffix
    formatted_date = date_only.strftime("%B ") + add_day_suffix(date_only.day) + date_only.strftime(", %Y")

    
    return formatted_date

def extract_Argued_date(text):
    # define a regular expression to match the date format
    date_pattern = r"Argued\s+([A-Za-z]+ \d{1,2}, \d{4})"

    # search for the date pattern in the text
    match = re.search(date_pattern, text)
    formatted_date = 0
    # if a match is found, extract the date and parse it to a datetime object
    if match:
        argued_date_str = match.group(1)
        argued_date = parse(argued_date_str)
        date_only = argued_date.date()
        formatted_date = date_only.strftime("%B ") + add_day_suffix(date_only.day) + date_only.strftime(", %Y")
#         print("Argued date:", formatted_date)
    else:
        print("No 'Argued' date found in the text.")
        
    return formatted_date

def extract_judge(text):
    # define a regular expression to match the text between "JUSTICE" and "delivered the opinion of the Court"
    pattern = r"JUSTICE\s+.*?delivered the opinion of the Court"

    # search for the pattern in the text
    match = re.search(pattern, text, re.DOTALL)

    # if a match is found, extract the text
    if match:
        extracted_text = match.group()
        # print(extracted_text)
    else:
        print("No match found.")
        
    return extracted_text


# Text Rendering
def replace_opinion_text(page_text, argued_date, case_name, judge_decision):
#     global condation
    # Find the text that starts with "No. " and ends with "delivered the opinion of the Court."
    match = re.search(r"No\..*delivered the opinion of the Court\.", page_text, re.DOTALL)
   # match.string
    replace_text = ""
    
    
    
    if match:
#         Case number coding 

        decide_text = match.group()
        decide_date_text = decide_text[decide_text.find("ON WRIT OF CERTIORARI"):decide_text.find("opinion of the Court")]
#         print(decide_date_text)
        
        case_num = match.group().split()[1]
        case1,case2 = case_num.split("–") 
        case1=int(case1)
#         print(case1)
        case2=str(case2)
        case1 = num2words(case1)
        # Convert each digit in the number to its spoken form
        case2 = "-".join([digit_mapping[d] for d in case2])


        decide_date = extract_Decide_date(decide_date_text)
        
        replace_text = f'{case_name}, Case Number {case1},  {case2}. On writ of certiorari to the United States Court of Appeals for the Federal Circuit. Argued {argued_date}  Decided {decide_date}. {judge_decision} .'
        

        replace_text = page_text.replace(match.group(), replace_text)

    
    
    return replace_text


## Text Rendering--->> Removal of some text from 1st Paragraph
def remove_firstpage_text(page_text):
    # Define the start and end patterns for extraction
    # Define the start and end patterns for extraction
    start_pattern = r'Cite as:.*?Opinion of the Court'
    end_pattern = r'SUPREME COURT OF THE UNITED STATES'
    extracted_text = re.sub(start_pattern + '(.*?)' + end_pattern, '', page_text, flags=re.DOTALL)
    
    return extracted_text
    
## Finding Text --> 
def find_text(texts):
#     pattern = r"Cite as: 598 U\. S\. ____ \(2023\) Opinion of the Court NOTICE: .*? SUPREME COURT OF THE UNITED STATES"
    pattern = r"Cite as: \d+ U\. S\. ____ \(\d+\) \d+ Opinion of the Court NOTICE: .*? SUPREME COURT OF THE UNITED STATES"
    
    matches = 0
    for i, text in enumerate(texts):
        match = re.search(pattern, text)
        if match:
            extracted_text = match.group(0)
            matches = i

    return matches

## Remove Punctuation Marks
def remove_ellipices_hypens_linebreak(page_text):
    clean_pdf_text = []
    for i in range(len(page_text)):
        clean = str(page_text[i])
        clean_text = clean.replace('. . .', "")
        clean_text = clean_text.replace('\n', "")
        clean_text = clean_text.replace('\\n', "") 
        clean_text = clean_text.replace("[", "").replace("]", "") 
        clean_text = clean_text.replace("(", "").replace(")", "")
        clean_text = re.sub('([a-zA-Z])(\d)', r'\1 \2', clean_text)
        
        clean_pdf_text.append(clean_text)
          
    return clean_pdf_text

## Removal of all citation from pdf Text -->
def remove_citation(page_text):
    cleaned_pdf_text = []
    id_pattern = re.compile(r'(\s|^)(I|i)d\.?,?\s*(at)?\s*\d+(?:-\d+)?\.?(\s|$)')
    regex_see = r"\b(See\s+[^.]*\.)\s*[^.]*\."
    regex_see_eg = r"\b(See,\s*e\.g\.,\s+[^.]*\.)\s*[^.]*\."
    regex_ibid = r"\b(Ibid\.\s*(?:at\s+\d+\s*)?)"
    pattern_at = r"\b\d{4} slip op\.,? (?:at )?\d+\b"
    for i in range(len(page_text)):
        clean_text = re.sub(regex_see, "", page_text[i])
        clean_text = re.sub(regex_see_eg, "", clean_text)
        clean_text = re.sub(regex_ibid, "", clean_text)
        clean_text = re.sub(pattern_at, "", clean_text)
        clean_text = id_pattern.sub('', clean_text)
        
        cleaned_pdf_text.append(clean_text)
        
    return cleaned_pdf_text


# Making some of the text in suitable format
def make_text_suitable(page_text):
    # Combine the regular expressions into one pattern
    cleaned_text = []
    for i in range(len(page_text)):
        
        clean_text = page_text[i].replace("U. S. C.", "USC").replace("U. S.", "US")
        cleaned_text.append(clean_text)
        
    return cleaned_text       


# Roman Digits to "Part 1, 2, ...."
def remove_roman_digit(page_text):
    roman_digits = r'\b([IVXLCDM]+)\b'

    numeral_to_text = {
        'I': '{{Part 1}}',
        'II': '{{Part 2}}',
        'III': '{{Part 3}}',
        'IV': '{{Part 4}}',
        'V': '{{Part 5}}',
        'VI': '{{Part 6}}',
        'VII': '{{Part 7}}',
        # add more mappings as needed
    }
    
    cleaned_pdf_text = []
    for i in range(len(page_text)):
        cleaned_text = re.sub(roman_digits, lambda m: numeral_to_text.get(m.group(1), m.group(1)), page_text[i])
        cleaned_pdf_text.append(cleaned_text)
        
    return cleaned_pdf_text

## Coverting into desired format given in docs file.
def roman_digit_format(page_text):
    pattern = r"Part \d [A-Z]?$" # Updated regex pattern
    clean_text = []
    for i in range(len(page_text)):
        if re.search(pattern, page_text[i]): # Check if the pattern matches
            replaced_text = re.sub(r"(Part \d) ([A-Z])?", r"{{\1, \2}}", page_text[i]) # Use original replacement pattern
        else:
            replaced_text = re.sub(r"(Part \d)", r"{{\1}}", page_text[i]) # Replace only "Part 1"
            
        clean_text.append(replaced_text)
        
    return clean_text


## Remaining Citation Removal
def remove_all_citation(page_text):
    # Define regular expressions for each type of citation
    regex_usc = r"\b\d+\s+U\.\s*S\.\s*C\.\s+§§?\d+(?:\s*\(\w+\))?"
    regex_citation = r"\b\d+\s+U\.\s*S\.\s+___(?:\s*\(\w+\))?"
    regex_slip_op = r"\(slip\s+op\.,\s+at\s+\d+\)"

    # Combine the regular expressions into one pattern
    combined_regex = r"(" + regex_usc + r"|" + regex_citation + r"|" + regex_slip_op + r")"
    cleaned_text = []
    for i in range(len(page_text)):
        clean_text = re.sub(combined_regex, "", page_text[i])
        cleaned_text.append(clean_text)
        
    return cleaned_text

# Some other Unnessacearry Punctuation
def remove_unnessecary_punctuation(page_text):
    cleaned_text = []
    for i in range(len(page_text)):
        clean = str(page_text[i])
        puct_remove = clean.replace(', ,', '').replace(',  ,', '')
        puct_remove = puct_remove.replace(',', '')
        puct_remove = puct_remove.replace('“', '').replace('”', '') 
        puct_remove = puct_remove.replace('‘', '') #.replace('', '') 
        cleaned_text.append(puct_remove)
        
    return cleaned_text


def remove_US_Citations(pdf_text):
    pattern =r'\d+\s+U\.\s+S\.\s+(?:\d+\s+)*\d+?(?=\s+\d|$)'
    pattern_ = r'\d+\s+U\.\s+S\.\s+'
    pattern_v1 = r'\d+\s+U\.\s+S\.\.\s+'
    clean_pdf = []
    for text in pdf_text:
        cln = re.sub(pattern, "", text)
        cln_ = re.sub(pattern_, "", cln)
        cln_ = re.sub(pattern_v1, "", cln_)
        clean_pdf.append(cln_)
        
    return clean_pdf  

# 
def swap_name_justice(match):
    name = match.group(1).strip()
    name = name.lower().capitalize()
    print(name.lower().capitalize())
#     if 
#     names = match.group(1).strip()
#     print(names)
    justice = match.group(2).strip()
    return f"{justice}, {name}"


def remove_USC_citation(pdf_text):
    pattern = r'\d+\sU.\sS.\sC.\s§§?\d+\s?\w*'
    
    clean_pdf_text = []
    
    for text in pdf_text:
        new_text = re.sub(pattern, '', text)
        
        clean_pdf_text.append(new_text)
        
    return clean_pdf_text

def remove_at_slip_cite(pdf_text):
#     pattern_ = r'(?:slip op. at \d+ )?(at| at \d+|slip op\. at \d+)'
    pattern_ = r'(?:slip op.)|(?:slip op. at \d+ )?(at \d+|slip op\. at \d+)'
    clean_pdf_text = []
    for text in pdf_text:
        cln_text = re.sub(pattern_, "", text)
        clean_pdf_text.append(cln_text)
        
    return clean_pdf_text


def remove_Name_v_Name_cite(pdf_text):
    pattern = r"([A-Za-z\s]+) v\. ([A-Za-z\s]+)"
    pattern_ = r"([A-Za-z\s]+) v\. ([A-Za-z\s]+) (\d{4})"
    
    clean_text = []
    for text in pdf_text:
        cln = re.sub(pattern_, "", text)
        cln = re.sub(pattern, "", cln)
        clean_text.append(cln)
        
    return clean_text


def remove_opinonofCourt(page_text):
    cleaned_text = []
    for text in page_text:
        text = text.replace("Opinion of the Court", "")
        text = text.replace("Cite as:", "")
        cleaned_text.append(text)
        
    return cleaned_text
        

def Remove_Brief_Citation(pdf_text):
    pattern = r"\b((?i)brief for\s+[^.]*\.)\s*"
    pattern_of = r"\b((?i)brief of\s+[^.]*\.)\s*"
    clean_pdf = []
    for text in pdf_text:
        cln = re.sub(pattern, "", text)
        cln_ = re.sub(pattern_of, "", cln)
        
        clean_pdf.append(cln_)
        
    return clean_pdf


# Reading pdf -> Cleaning Text -> Extracting Clean Text
def clean_pdf(path):
    text_list = []
    with pdfplumber.open(path) as pdf_file:
        for page in pdf_file.pages:
            text = page.extract_text()
            text_list.append(text)

    return text_list



def Cleaned_Pdf_Text(path):
    text_list = clean_pdf(path)
    for i in range(len(text_list)):
        text_list[i] = text_list[i].replace('\n', ' ')
    
    for i in range(len(text_list)):
        text_list[i] = text_list[i].replace("- ", '')
    
    date = extract_Argued_date(text_list[0])

    new_pdf_text = remove_footer(text_list)
    page_number = find_text(new_pdf_text)
    case_name = name_extract(str(new_pdf_text[page_number+1]))
    case_name = case_name.split("2 ")[1]

    case_name_1 = case_name.split(' versus')[0]
    case_name_2 = case_name.split('versus ')[1].lower().capitalize()
    case_name_1 = case_name_1.lower().capitalize()
    print(case_name_1)
    print(case_name_2)
    case_name_upd = case_name_1+ ' versus '+ case_name_2
    justice_text = str(text_list[page_number-1])

    extracted_text = ''
    if 'affirmed' in justice_text:
        group = justice_text.split('affirmed.')[1]
        extracted_text = group
        # print(group)
    elif 'remanded.' in justice_text:
        group = justice_text.split('remanded.')[1]
        extracted_text = group
        # print(group)
    
    extracted_text = extracted_text.replace('C. J.', 'Chief Justice').replace('JJ.', 'Justices')
    extracted_text = extracted_text.replace('J.', 'Justice')

    Judge_text = re.sub(r"(\b\w+), (Justice|Chief Justice|Justices)", swap_name_justice, extracted_text)
    
    # Rendered First Paragraph
    rep_text = replace_opinion_text(str(new_pdf_text[page_number]), date, case_name_upd, Judge_text)

    new_pdf_text[page_number] = str(rep_text) 

    text_extract = remove_firstpage_text(str(new_pdf_text[page_number]))

    new_pdf_text[page_number] = text_extract

    for i in range(len(new_pdf_text)):
        new_pdf_text[i] = new_pdf_text[i].replace('-', ' ').replace('—', ' ')

    test_pdf_v1 = remove_ellipices_hypens_linebreak(new_pdf_text)

    test_pdf_v1 = remove_unnessecary_punctuation(test_pdf_v1)

    case_name_ = case_name.replace('versus', 'v.')

    for i in range(len(test_pdf_v1)):
        test_pdf_v1[i] = test_pdf_v1[i].replace(f'{case_name_}', '')

    

    test_pdf_v1 = remove_USC_citation(test_pdf_v1)

    for i in range(len(test_pdf_v1)):
        test_pdf_v1[i] = test_pdf_v1[i].replace('Cite as:', '').replace('Opinion of the Court', '')

    test_pdf_v1 = remove_pageNumber(test_pdf_v1)

    for i in range(len(test_pdf_v1)):
        test_pdf_v1[i] = test_pdf_v1[i].replace('§', '§ ')

    for i in range(len(test_pdf_v1)):
        test_pdf_v1[i] = test_pdf_v1[i].replace('§ §', '§§')

    test_pdf_v1 = remove_roman_digit(test_pdf_v1)

    # test_pdf_v1 = roman_digit_formatsss(test_pdf_v1) 

    test_pdf_v1 = remove_citation(test_pdf_v1)

    test_pdf_v1 = remove_at_slip_cite(test_pdf_v1)

    test_pdf_v1 = remove_US_Citations(test_pdf_v1)

    test_pdf_v1 = remove_Name_v_Name_cite(test_pdf_v1)

    # test_pdf_v1 = Remove_Brief_Citation(test_pdf_v1)

    # removing Syllabus Pages
    clean_pdf_text = []
    for i in range(page_number, len(test_pdf_v1)):
        clean_pdf_text.append(test_pdf_v1[i])
      
    return clean_pdf_text


def store_to_Pdf(pdf_text, output_path):
    # open a file in write mode
    with open(output_path, 'w') as file:
        # loop over the list and write each element to the file
        for item in pdf_text:
            file.write(item + '\n')

    # close the file
    file.close()



input_path = "D:\\Hamid Work\\Test\\1. Arellano v. McDonough (1).pdf"

# path = '3. Helix Energy Solutions Group v. Hewitt.pdf'
# 
# output_path = "D:\\Hamid Work\\Test\\Output_test_files\\Clean_Arellano Versus McDonough_v1.pdf"

# pdf_text = clean_pdf(path)

# clean_pdf_text = Cleaned_Pdf_Text(input_path)

# store_to_Pdf(clean_pdf_text, output_file=output_path)

# if len(sys.argv)<3:
#     print("Usage: python your_script.py input_path output_path")
#     sys.exit(1)

# arg1_F1 = sys.argv[1]
# arg2_F1 = sys.argv[2]

# clean_pdf_text = Cleaned_Pdf_Text(arg1_F1)

# store_to_Pdf(clean_pdf_text, output_path=arg2_F1)