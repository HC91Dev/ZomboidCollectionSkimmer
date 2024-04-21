import time
import requests
from bs4 import BeautifulSoup
import re

def extract_mod_id(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        mod_id_element = soup.find('div', class_='workshopItemDescription')
        
        if mod_id_element:
            mod_id_html = mod_id_element.prettify()
            # Find Mod ID pattern with newline characters or <br/> tags
            mod_id_match = re.search(r'Mod\s*ID\s*:\s*([^<\n]+)', mod_id_html, re.IGNORECASE)
            if mod_id_match:
                # Extract the mod_id from the match
                mod_id = mod_id_match.group(1).strip()
                return mod_id
            else:
                return None
        else:
            return None
    except Exception as e:
        print("An error occurred:", e)


def extract_workshop_id(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            description_tag = soup.find('div', class_='workshopItemDescription')
            if description_tag:
                workshop_id_match = re.search(r'id=(\d+)', url).group(1)
            return workshop_id_match
        else:
            print("Failed to fetch URL:", url)
    except Exception as e:
        print("An error occurred:", e)

def extract_all_hrefs(url):
    hrefs = set()  # Use a set to store unique hrefs
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            description_tag = soup.find('div', class_='collectionChildren')
            if description_tag:
                all_a_tags = description_tag.find_all('a')
                for a_tag in all_a_tags:
                    href = a_tag.get('href')
                    if href and "sharedfiles" in href and href not in hrefs:
                        hrefs.add(href)  # Add href to set if not already present
                return list(hrefs)  # Convert set back to list before returning
        else:
            print("Failed to fetch URL:", url)
    except Exception as e:
        print("An error occurred:", e)

def main():
    start_time = time.time()
    collection_url = input("Enter the collection URL: ")
    try:
        links = extract_all_hrefs(collection_url)
    except Exception as e:
        print("Failed to fetch URL:", collection_url)
        print("Error:", e)
        return
    
    mod_ids = set()
    workshop_ids = set()

    for link in links:
        mod_id = extract_mod_id(link)
        workshop_id = extract_workshop_id(link)

        if mod_id:
            mod_ids.add(mod_id)  

        if workshop_id:
            workshop_ids.add(workshop_id)  

    with open("mod_workshop_ids.txt", "a+") as file:
        existing_ids = set(file.read().splitlines())

        new_mod_ids = mod_ids - existing_ids
        new_workshop_ids = workshop_ids - existing_ids

        if new_mod_ids:
            print("New Mod IDs:", new_mod_ids)
            file.write(";".join(new_mod_ids))
            file.write("\n")  

        if new_workshop_ids:
            print("New Workshop IDs:", new_workshop_ids)
            file.write(";".join(new_workshop_ids))
            file.write("\n")

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.2f} seconds")

if __name__ == "__main__":
    main()
