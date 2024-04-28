import csv
import PyPDF2
import re
import os


def extract_text_from_pdf(file_path):
    text = ''
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text

def extract_recognized_clubs_from_text(text):
    recognized_clubs = {}
    # lines = text.split('\n')
    lines = re.split(r'\n|\.\.\.', text)
    # print(lines)
    club_name = ''
    club_description = ''
    status = ''
    for i in range(len(lines)):
        line = lines[i].strip()
        if 'Recognized' in line or 'Not Recognized' in line or 'Renewing Recognition' in line:
            
            club_name = lines[i - 1].strip()
            if 'http' in line:
                club_link, status = lines[i].strip().split('•')
            else:
                club_link, status = '', lines[i].strip()
            club_description = ''
            j = i + 1
            while j < len(lines)-1 and not('Recognized' in lines[j+1].strip() or 'Renewing Recognition' in lines[j+1].strip() or 'Not Recognized' in lines[j+1].strip()):
                club_description += lines[j]
                j += 1
            recognized_clubs[club_name] = {'Link': club_link, 'Status': status, 'Description': club_description + '...'}
    return recognized_clubs

def process_folder(folder_path, output_file):
    recognized_clubs_all = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            print(filename, ' loaded')
            file_path = os.path.join(folder_path, filename)
            pdf_text = extract_text_from_pdf(file_path)
            recognized_clubs = extract_recognized_clubs_from_text(pdf_text)
            recognized_clubs_all.update(recognized_clubs)

    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Club Name', 'Link','Status', 'Description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for club_name in recognized_clubs_all:
            # print(club_name)
            writer.writerow({'Club Name': club_name, 'Link': recognized_clubs_all[club_name]['Link'],'Status': recognized_clubs_all[club_name]['Status'], 'Description': recognized_clubs_all[club_name]['Description']})

folder_path = 'data/orgs'  
output_file = 'recognized_clubs.csv'  # Output CSV file
process_folder(folder_path, output_file)
print("CSV file created successfully!")
