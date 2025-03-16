#------
# Author: Virag Umathe, Dr Rosa Filgueira
# Discription: The code uses OpenAIs chatGPT-4o for the article extraction task on the dataset prepared on The Spiritualist.
#
# File I/O: -> Code needs "json_collector" in the same directory. "json_collector" is the directory which contains the extracted json from the xml files. 
#           -> The code produces json filess which will conatins the article according to the paper id.
#
#
#------


# Imports (in alphabetic order)
import json
import openai
import os   
import tiktoken
from tqdm import tqdm
from typing import Union



# Setting up the api key from the UoE
client = openai.OpenAI(
    api_key="<PASTE YOUR API KEY HERE>",
    
)

# Function for generating the response from the GPT-4o.
# Return: String of the text which will be the response generated from the GPT
# Args: paper_id = Id of the paper to keep the track of the paper, 
#             news_paper_text = String as a text which will be passed to the GPT
def generate_response(paper_id, news_paper_text) -> str:

    system_content = f"""
                    I have extracted the medieval Scottish newspaper texts and I have a plain text.
                    Your job is to extract the different features in the text like contents, articles, and other things like advertisements. First analyse the whole text and then take these features out.
                    The name of the newspaper is THE SPIRITUALIST so the title names will not be as same as the newspaper name.

                    While working make sure to follow the following things the conditions written in all capital are negotiable

                    1. Dont add any of your output just give me the necessary things like the Article title and then the article
                    2. If the text is all capitalised it is more likely to be the title of the article
                    3. MAKE SURE THE TITLE NAME WILL ALWAYS BE CAPITAL IN THE PROVIDED CONTENT AND CHOOSE THE TEXT ACCORDINGLY.
                    4. You are not allowed to change the casing of the content at all
                    5. Don't summarise the text use each and every text in the output.
                    6. DONT ADD ANY OF YOUR TEXT IN THE OUTPUT
                    7. I am passing you the whole text in two chunks make sure you will mention the page number in the output so that I can extract it later.
                    8. If the article span is more than 1 page then mention multiple pages too.
                    9. If you are getting long long text you are NOT allowed to ignore the small articles. YOU HAVE TO PROCESS EACH AND EVERY ARTICLE.
                    10. Article name must be in the all caps so while parsing the data make sure the article title will be in capital in a given text.
                    11. Don't add content of the paper in the article. And dont extract index of the paper as an article. You re extracting the index of the paper for the article
                    12. Dont terminate the output extract the articles from the whole text and give it.
                    
                    Format as strict JSON enclosed in <JSON> tags:
                    <JSON>
                    {{"{paper_id}": [
                            {{"Page  Number" : <Update the Page Number here>, "title": "Example Article 1", "text": "Example text 1"}},
                            {{"Page  Number" : <Update the Page Number here>, "title": "Example Article 2", "text": "Example text 2"}}
                        ]
                    }}
                    </JSON>
                    

                """

    user_content = f"Here is the newspaper text you have to extract {news_paper_text}"

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content}
    ]
    
    response = client.chat.completions.create(model="gpt-4o",
                                            messages=messages,
                                            temperature=0.0,
                                            top_p=1.0,
                                            frequency_penalty=0.0,
                                            presence_penalty=0.1
                                            )
    
    content = response.choices[0].message.content
    
    return content


# Function Yields JSON filenames one by one from the given directory.
# Return: Name of the file
# Args: Name of the directory
def get_json_filenames(directory) -> str:

    for filename in os.listdir(directory)[0:5]:
        if filename.endswith(".json"):
            yield filename



# Function reads a JSON file and returns the values of two hardcoded keys.
# Returns: tuple: Values of the two hardcoded keys.    
# Args: file_path (str): Path to the JSON file.
def get_json_text(file_name) -> Union[tuple, tuple]:
    
    with open(file_name, 'r') as file:
        data = json.load(file)  # Load the JSON content
        
        # Hardcoded keys
        key1 = "paper_id"
        key2 = "text"
        
        # Accessing the values of the hardcoded keys
        value1 = data.get(key1, None)  # If the key doesn't exist, return None
        value2 = data.get(key2, None)  # Same for the second key
        
        return value1, value2


# The function splits the text into two halves based on token count.
# Returns a dictionary with 'first_half' and 'second_half'
# Args: text: text as a string for splitting it as per the tokens
#       max_tokens: Maximum number of tokens to make sure the split is necessary
def split_text(text, max_tokens) -> dict:

    enc = tiktoken.encoding_for_model("gpt-4")  # Adjust for your model
    tokens = enc.encode(text)
    total_tokens = len(tokens)

    if total_tokens <= max_tokens:
        return {"first_half": text, "second_half": ""}  # No need to split if within limit

    mid_point = total_tokens // 2
    first_half_tokens = tokens[:mid_point]
    second_half_tokens = tokens[mid_point:]

    first_half = enc.decode(first_half_tokens)
    second_half = enc.decode(second_half_tokens)

    splitted_text = {"first_half": first_half, "second_half": second_half}

    return splitted_text

# Appends the GPT response to the existing JSON file and extracts the last two key-value pairs.
# Returns: dictonery of the last two entries, the previous json
# Args: gpt_response: Response from the GPT
#       previous_json: previous json as string
def process_gpt_output(gpt_response, previous_json) -> Union[dict, str]:
    
    previous_json.update(gpt_response)  # Merge new response

    # Extract the last two key-value pairs
    last_two_entries = dict(list(previous_json.items())[-2:])

    return last_two_entries, previous_json


# Function extracts the last article's title and text as a formatted string.
# Returns: String containing the last article's title and text.
# Args: json_data (dict): JSON dictionary containing articles.
def get_last_entry_as_string(json_data):
    if "articles" in json_data and json_data["articles"]:
        last_article = json_data["articles"][-1]  # Get the last article
        return f"{last_article['title']}, {last_article['text']}"
    return ""  # Return empty string if no articles exist


# Function saves a dictionary to a JSON file, appending values if keys exist.
# Returns: data_dict (dict): Dictionary containing data to be saved.
# Args: file_path (str): Path to the JSON file.
def save_to_json(file_path, data_dict) -> None:
    """
    Save the dictionary to a JSON file. If the key exists, append the values.
    Otherwise, create a new key with the provided values.
    
    Args:
        file_path (str): Path to the JSON file.
        data_dict (dict): The dictionary containing the data to be saved.
    """
    # Check if the JSON file exists
    if os.path.exists(file_path):
        # If the file exists, load the current data
        with open(file_path, 'r') as file:
            current_data = json.load(file)
    else:
        # If the file does not exist, start with an empty dictionary
        current_data = {}

    # Loop through the dictionary to append values or create new keys
    for key, value in data_dict.items():
        # If the key exists, append the value
        if key in current_data:
            current_data[key].append(value)
        else:
            # If the key does not exist, create it with the value
            current_data[key] = [value]

    # Save the updated dictionary back to the file
    with open(file_path, 'w') as file:
        json.dump(current_data, file, indent=4)
        

# Function processes a paper's text by splitting it, generating responses, and saving results.
# Returns: text (str): The text content of the paper.
# Args: paper_id (str): Unique identifier for the paper.
def utils(paper_id, text) -> None:

    json_dump_lst = []

    split_data = split_text(text, 2500)
    first_half, second_half = split_data["first_half"], split_data["second_half"]
    
    first_response = generate_response(paper_id, first_half)
    first_response = first_response.replace("</JSON>", "").replace("<JSON>", "")
    local_json_first_temp = json.loads(first_response)
    json_dump_lst = local_json_first_temp[paper_id]
    temp_text = get_last_entry_as_string(local_json_first_temp)
    second_text = temp_text + second_half
    second_response = generate_response(paper_id, second_text)
    response_second = second_response.replace("</JSON>", "").replace("<JSON>", "")
    second_json_to_add = json.loads(response_second)
    json_dump_lst.extend(second_json_to_add[paper_id])
    local_json_data[paper_id] = json_dump_lst
    save_to_json(f"output/{paper_id}", local_json_data)




# Run the code.
directory_path = "json_collector/"

local_json_data = {}



for filename in tqdm(get_json_filenames(directory_path)):

    print(filename)

    real_path = f"json_collector/{filename}"

    paper_id, text = get_json_text(real_path)
    
    print(paper_id)
    
    try:
        utils(paper_id, text[0:20000])

    except Exception as e:
        print(f"Something happened to the paper_id: {paper_id}")
        print(f"Error is: {e}")





