# The-Spiritualist

Download the whole dataset from [here](https://data.nls.uk/data/digitised-collections/spiritualist-newspapers/)

---

## XML to JSON converstion with pages and whole text

### Overview

This project is designed to extract metadata and text from XML files, convert them to structured JSON format, and save the results as JSON files. The metadata is extracted from a CSV file (`spiritualist_issue_data.csv`), while the text is extracted from XML files in the ALTO format. The converted data is then merged with metadata and saved into a final JSON file, ready for further processing or analysis.

### Features

- Extracts paper metadata using the paper's unique ID from a CSV file.
- Converts ALTO XML files to JSON format by parsing the XML structure.
- Merges metadata and text from the XML files into a single JSON object.
- Saves the processed data as a JSON file for each paper.

### Requirements

- Python 3.x
- Pandas
- tqdm
- xml.etree.ElementTree (included in Python's standard library)

### Usage
Run the script to extract the xml files and create the json.
~~~
python pre_process_xml.py
~~~

### File Structure

- **`spiritualist_issue_data.csv`**: A CSV file containing metadata for each paper. This file is used to retrieve additional metadata based on the paper ID.
- **`text_dir/`**: A directory containing subdirectories for each paper, with XML files in ALTO format (located in `alto/`).
- **`merged_output_{paper_id}.json`**: The resulting JSON files that contain the extracted metadata and text.

### Functions

#### 1. `get_paper_data(paper_id)`

Retrieves metadata for a given paper ID from the `spiritualist_issue_data.csv` file.

**Args**:  
- `paper_id` (str): The unique identifier for the paper.

**Returns**:  
- Dictionary containing metadata for the given paper.

#### 2. `xml_to_json(file_path)`

Converts an XML file to a JSON dictionary.

**Args**:  
- `file_path` (str): Path to the XML file.

**Returns**:  
- Dictionary containing the parsed XML data.

#### 3. `save_json_to_file(json_data, output_path)`

Saves a JSON dictionary to a file.

**Args**:  
- `json_data` (dict): The JSON data to be saved.
- `output_path` (str): Path to the output JSON file.

#### 4. `process_json(json_object, folder_path)`

Processes the XML-to-JSON converted dictionary to extract text and metadata.

**Args**:  
- `json_object` (dict): The raw JSON-converted XML data.
- `folder_path` (str): Path to the folder where the XML files are stored.

**Returns**:  
- Processed JSON dictionary containing structured text and metadata.

#### 5. `process_folder(folder_path_raw, output_file)`

Processes all XML files in a folder and saves the extracted data as a merged JSON.

**Args**:  
- `folder_path_raw` (str): Path to the folder containing XML files (subfolders for each paper).
- `output_file` (str): Path where the output JSON file should be saved.

### Usage

#### Example Usage

1. Place the `spiritualist_issue_data.csv` file in the root directory.
2. Place the XML files for each paper in their respective subdirectories under the `text_dir` directory.
3. Run the script

The script will process all directories inside `text_dir/`, extract metadata, and convert the XML files to JSON format. It will then save the processed data into JSON files named `merged_output_{paper_id}.json` for each paper.

### Folder Structure Example

```
text_dir/
│
├── paper1/
│   └── alto/
│       ├── file1.xml
│       └── file2.xml
│   └── merged_output_paper1.json
│
├── paper2/
│   └── alto/
│       ├── file1.xml
│       └── file2.xml
│   └── merged_output_paper2.json
└── ...
```

### Notes

- The XML files should follow the ALTO XML format.
- Each paper should have a corresponding subdirectory in `text_dir/` containing its XML files.
- The metadata is matched to each paper using the paper's unique ID from the `spiritualist_issue_data.csv` file.
---

## Article Extraction Using GPT-4o


### Description
This repository contains a script that utilizes OpenAI's GPT-4o to extract articles from a dataset prepared on *The Spiritualist* newspaper. The extracted content is formatted as JSON files for further processing.

### Features
- Parses JSON files containing newspaper text.
- Uses GPT-4o to extract articles, preserving their original formatting.
- Splits large text into manageable chunks for processing.
- Saves extracted articles in structured JSON format.

### Prerequisites
- Python 3.x
- OpenAI API key
- Required Python packages (see installation steps below)


### Setup
Ensure you have the OpenAI API key configured:

```python
client = openai.OpenAI(
    api_key="<PASTE YOUR API KEY HERE>"
)
```

Also, make sure your dataset is placed inside the `json_collector/` directory.

### Usage
Run the script to process and extract articles

~~~
python extract_article.py
~~~

### Input
- JSON files stored in `json_collector/` directory, extracted from XML files.
- Each JSON file should contain:
  ```json
  {
      "paper_id": "example_id",
      "text": "Full text of the newspaper..."
  }
  ```

### Output
- Processed JSON files will be saved in the `output/` directory.
- Example output format:
  ```json
  {
      "example_id": [
          {
              "title": "EXAMPLE ARTICLE 1",
              "text": "Example text 1"
          },
          {
              "title": "EXAMPLE ARTICLE 2",
              "text": "Example text 2"
          }
      ]
  }
  ```

### Key Functions
- `generate_response()`: Calls GPT-4o to extract articles.
- `split_text()`: Splits large text blocks for processing.
- `get_json_filenames()`: Fetches JSON filenames from the dataset directory.
- `get_json_text()`: Extracts newspaper text from JSON files.
- `get_last_entry_as_string()`: Retrieves the last processed article.
- `save_to_json()`: Stores extracted data in JSON format.
- `utils()`: Orchestrates the processing pipeline.

---
