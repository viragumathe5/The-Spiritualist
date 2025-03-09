
#------
# Author: Virag Umathe, Dr Rosa Filgueira
# Discription: The code extracts the XML files to get the jsons for the processing in the gpt.
#
# File I/O: -> Code needs The Spiritualist csv for getting the metadata, and all the alto directires inside the directries with paper id. 
#           -> The code produces jsons files which will conatines the text extracted from the meta data.
#
#
#------


# Imports (in alphabetic order)

import collections
import json
import os
import pandas as pd
from tqdm import tqdm
import xml.etree.ElementTree as ET



# Function retrieves metadata for a given paper ID from a CSV file.
# Returns: Dictionary containing metadata for the given paper ID.
# Args: paper_id (str): The unique identifier for the paper.
def get_paper_data(paper_id) -> dict:

    data_json = {}

    data_frame = pd.read_csv("spiritualist_issue_data.csv")

    json_data = data_frame.set_index("newspaper_id").to_dict(orient="index")

    try:
        temp_json = json_data[int(paper_id)]
    
    except:

        temp_json = json_data[int(0)]
   
    return temp_json


# Function converts an XML file to a JSON dictionary.
# Returns: Dictionary containing the parsed XML data.
# Args: file_path (str): Path to the XML file.
def xml_to_json(file_path):

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        def parse_element(element):
            """Recursively parses an XML element into a dictionary."""
            parsed_data = {}
            # Add element attributes if present
            if element.attrib:
                parsed_data.update({f"@{k}": v for k, v in element.attrib.items()})
            # Add element text if present
            if element.text and element.text.strip():
                parsed_data["#text"] = element.text.strip()
            # Recursively parse child elements
            children = list(element)
            if children:
                child_data = {}
                for child in children:
                    child_name = child.tag.replace("{http://www.loc.gov/standards/alto/v3/alto.xsd}", "")
                    child_parsed = parse_element(child)
                    if child_name in child_data:
                        if not isinstance(child_data[child_name], list):
                            child_data[child_name] = [child_data[child_name]]
                        child_data[child_name].append(child_parsed)
                    else:
                        child_data[child_name] = child_parsed
                parsed_data.update(child_data)
            return parsed_data

        json_data = {root.tag.replace("{http://www.loc.gov/standards/alto/v3/alto.xsd}", ""): parse_element(root)}
        return json_data
    except ET.ParseError as e:
        print(f"Error parsing {file_path}: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error with {file_path}: {e}")
        return {}


# Function saves a JSON dictionary to a file.
# Args: json_data (dict): JSON data to be saved.
#       output_path (str): Path to the output JSON file.
def save_json_to_file(json_data, output_path):

    try:
        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(json_data, json_file, indent=4, ensure_ascii=False)
            print(f"JSON file saved to {output_path}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")


# Function processes an XML-to-JSON converted dictionary to extract text and metadata.
# Returns: Processed JSON dictionary containing structured text and metadata.
# Args: json_object (dict): Dictionary containing raw JSON-converted XML data.
#       folder_path (str): Path to the folder where the XML files were stored.
def process_json(json_object, folder_path) -> dict:

    new_json = {}
    text_json = {}
    big_text_list = []
    final_json = {}
    paper_text = []

    for keys, values in json_object.items():
        
        new_json[values["alto"]["Layout"]["Page"]["@ID"]] = values["alto"]["Layout"]["Page"]["PrintSpace"]["TextLine"]

    sorted_data = dict(sorted(new_json.items(), key=lambda item: int(item[0][4:])))
    
    #sorted_data = dict(sorted(new_json.items(), key=lambda item: int(item[0].lower().lstrip("page"))))
        
        #sorted_data = dict(sorted(new_json.items(), key=lambda item: int(item[0].lstrip("page").split("_")[0])))

    for filtered_keys, filtered_values in sorted_data.items():

        text_list = []

        for elements in filtered_values:

            if type(elements["String"]) == list:     
                for content in elements["String"]:
                    text_list.append(content["@CONTENT"])
            else:
                text_list.append(elements["String"]["@CONTENT"])

        merged_text = " ".join(text_list)
        
        text_json[filtered_keys] = merged_text

        paper_text.append(merged_text)

    for text in text_json.values():

        final_json["paper_id"] = folder_path

    final_json.update(get_paper_data(folder_path))
    final_json.update(text_json)
    final_json["text"] = " ".join(paper_text).replace("\\", "")
    
    return final_json

# Function processes all XML files in a folder and saves the extracted data as JSON.
# Args: folder_path_raw (str): Path to the folder containing XML files.
#       output_file (str): Path where the output JSON file should be saved.    
def process_folder(folder_path_raw, output_file):

    print(folder_path_raw)

    merged_data = {}

    folder_path = folder_path_raw + "/alto/"
    
    files = [f for f in os.listdir(folder_path) if f.endswith(".xml")]

    for idx, file_name in enumerate(tqdm(files, desc="Processing files"), start=1):
        file_path = os.path.join(folder_path, file_name)
        json_data = xml_to_json(file_path)
        merged_data[f"page_{idx}"] = json_data

    merged_data = process_json(merged_data, folder_path_raw)

    save_json_to_file(merged_data, output_file)

# Example Usage
if __name__ == "__main__":

    error_dict = []

    directory = "text_dir"
    
    directories = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f)) and f != '.ipynb_checkpoints']

    print(directories)
    
    for dir in tqdm(directories):
        folder_path = dir #os.path.join(directory, dir)  # Correctly join the path to the folder
        output_file = f"{dir}/merged_output_{dir}.json"  # Desired output JSON file path

        process_folder(folder_path, output_file)