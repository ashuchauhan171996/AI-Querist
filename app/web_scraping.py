import requests
from bs4 import BeautifulSoup
import csv

# Function to extract data from a webpage with a given index ID
def extract_data(index_id):
    url = f"https://stuactonline.tamu.edu/app/organization/profile/public/id/{index_id}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        if soup.find(class_="form-view"):
            # Extract data from the HTML
            print(url)
            try: organization_name = soup.find(class_="title").get_text().strip()
            except Exception as e: return None

            try: abbreviation = soup.find('dt', string='Abbreviation(s):').find_next_sibling('dd').string.strip()
            except Exception as e: abbreviation = None
            
            try: purpose = soup.find('dt', string='Purpose:').find_next_sibling('dd').string.strip()
            except Exception as e: purpose = None
                
            try: year_founded = soup.find('dt', string='Year Founded:').find_next_sibling('dd').string.strip()
            except Exception as e: year_founded = None
            
            try:  Membership_Dues= soup.find('dt', string='Membership Dues:').find_next_sibling('dd').string.strip()
            except Exception as e:  Membership_Dues = None
            
            try:  Admits_Members= soup.find('dt', string='Admits Members:').find_next_sibling('dd').string.strip()
            except Exception as e: Admits_Members = None
            
            try:  Meeting_Locations= soup.find('dt', string='Meeting Locations:').find_next_sibling('dd').string.strip()
            except Exception as e:  Meeting_Locations= None
            
            try:  Public_Contact_Name= soup.find('dt', string='Public Contact Name:').find_next_sibling('dd').string.strip()
            except Exception as e:  Public_Contact_Name= None
            
            try:  Public_Contact_Email_Address= soup.find('dt', string='Public Contact E-mail Address:').find_next_sibling('dd').string.strip()
            except Exception as e:  Public_Contact_Email_Address= None
            
            try:  Public_Contact_Phone_Number= soup.find('dt', string='Public Contact Phone Number:').find_next_sibling('dd').string.strip()
            except Exception as e:  Public_Contact_Phone_Number= None
            
            try:  Organization_Web_Site= soup.find('dt', string='Organization Web Site:').find_next_sibling('dd').string.strip()
            except Exception as e:  Organization_Web_Site= None
            
            try:  Organization_Email_Address= soup.find('dt', string='Organization E-mail Address:').find_next_sibling('dd').string.strip()
            except Exception as e:  Organization_Email_Address= None
            
            try:  Academic_Department= soup.find('dt', string='Academic Department:').find_next_sibling('dd').string.strip()
            except Exception as e: Academic_Department = None
            
            try:  Approximate_membership_of_the_organization= soup.find('dt', string='Approximate membership of the organization:').find_next_sibling('dd').string.strip()
            except Exception as e: Approximate_membership_of_the_organization = None
            
            try:  Membership_policies= soup.find('dt', string='Membership policies:').find_next_sibling('dd')
            except Exception as e:  Membership_policies= None
            
            try:  Weekly_time_committment = soup.find('dt', string='Weekly time committment required of organization members:').find_next_sibling('dd').string.strip()
            except Exception as e:  Weekly_time_committment= None
            
            try:  Domestic_US_Travel= soup.find('dt', string='Domestic US Travel:').find_next_sibling('dd').string.strip()
            except Exception as e:  Domestic_US_Travel= None
            
            try:  International_Travel= soup.find('dt', string='International Travel:').find_next_sibling('dd').string.strip()
            except Exception as e:  International_Travel= None
            
            
            # Return the extracted data as a dictionary
            return {
                'Organization Name' : organization_name,
                'Abbreviation': abbreviation,
                'Purpose': purpose,
                'Year Founded': year_founded,
                'Membership Dues': Membership_Dues,
                'Admits Members': Admits_Members,
                'Meeting Locations':Meeting_Locations,
                'Public Contact Name':Public_Contact_Name,
                'Public Contact E-mail Address':Public_Contact_Email_Address,
                'Public Contact Phone Number':Public_Contact_Phone_Number,
                'Organization Web Site': Organization_Web_Site,
                'Organization E-mail Address':Organization_Email_Address,
                'Academic Department': Academic_Department,
                'Approximate members in the organization':Approximate_membership_of_the_organization,
                'Membership policies': Membership_policies,
                'Weekly time committment required of organization members': Weekly_time_committment,
                'Domestic US Travel': Domestic_US_Travel,
                'International Travel':International_Travel,
                
                
                
                
                # Add more keys and values for additional data
            }
    else:
        print(f"Failed to fetch data from {url}")

# Function to write data to a CSV file
def write_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Organization Name','Abbreviation', 'Purpose', 'Year Founded','Membership Dues','Admits Members','Meeting Locations','Public Contact Name','Public Contact E-mail Address','Public Contact Phone Number','Organization Web Site','Organization E-mail Address','Academic Department','Approximate members in the organization','Membership policies','Weekly time committment required of organization members','Domestic US Travel','International Travel']  # Add more fieldnames as needed
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# Main function to loop through multiple index IDs and extract data
def main():
    index_ids = range(0,3000)  # Add more index IDs as needed
    all_data = []
    for index_id in index_ids:
        data = extract_data(index_id)
        if data:
            all_data.append(data)
    write_to_csv(all_data, 'organization_data.csv')

if __name__ == "__main__":
    main()
