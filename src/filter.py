#------
# Author: Virag Umathe, Dr Rosa Filgueira
# Discription: The code filters the JSONs for sending it to the GPT.
#
# File I/O: -> Code needs "json_collector" in the same directory. "json_collector" is the directory which contains the extracted json from the xml files. 
#           -> The code updates json filess which will conatins the paper id and paper number filtered output.
#
#
#------



# Imports in alphabetical order.
import json
import os
import re

# Dirctory for accessing the JSONs.
json_directory = "json_collector/"

# Function to clean the escape characters.
def clean_text(text):
    
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

# Function to clear OCR errors
def clean_ocr_text(text):
    
    pattern = r'[■«^:]+|(?<!\w)-|-(?!\w)'
    
    cleaned_text = re.sub(pattern, '', text)
    
    return cleaned_text


# Function to add the page number value infront of the every text and this will be the driving function for the above two function. 
def process_json_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            

            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            
            updated_text = ""
            for key in sorted(data.keys()):
                if key.startswith("Page"):
                    cleaned_page_text = clean_text(data[key])
                    cleaned_page_text = clean_ocr_text(cleaned_page_text)
                    updated_text += f" <{key}> {cleaned_page_text} "

            
            data["text"] = updated_text.strip()

            
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            print(f"Updated: {filename}")


process_json_files(json_directory)

