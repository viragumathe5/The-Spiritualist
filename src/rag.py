import openai
# from ranker import retrieve, rerank

client = openai.OpenAI(
    api_key="<>",
    
) 


def generate_answer(query, retrieved_docs):
    context = ""
    for i, doc in enumerate(retrieved_docs):
        context += f"[Doc {i+1}]\nTitle: {doc['title']}\nText: {doc['text']}\n\n"

    system_content = f"""
                     You are a RAG assistant for the 18th century newspaper called The Spiritualist 
                     I will be feeding you the document which will work as a content and you have to
                     give the answer according to that.
                     Make sure to not hallucinate and give the answer based on the content provided.
                     You can add your own knowledge but you cant change the information.  

                     You can answer in max 300 words if necessary.
                     But avoid giving very short answers.
                     You should tell things about the topic.
                    
                    Here is the contenxt {context}
                
                """


    

    user_content = f"Here is the newspaper text you have to extract {query}"

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

#"What is the Spiritualist newspaper about?"
#"Who is MR. MORSE?"
#"What happend to the the NATIONAL ASSOCIATION"
#"What happend to the office of the NATIONAL ASSOCIATION"
#"Why does FEMALE MEDICAL SOCIETY established?"
# ***** "What happened in the MEETING OF THE COUNCIL at BRITISH NATIONAL ASSOCIATION OF SPIRITUALISTS"
# "What was the FINANCE COMMITTEE’S REPORT"
# ***** "Tell me about the THE PSYCHOLOGICAL SOCIETY OF GREAT BRITAIN"


# query = "Tell me about the THE PSYCHOLOGICAL SOCIETY OF GREAT BRITAIN"

# retrieve_text = retrieve(query, top_k=20)
# ranked_docs = rerank(query, retrieve_text, top_k=5)

# paper_id_dict = {}

# for doc in ranked_docs:

#     paper_id_dict[doc["id"]] = doc["page_number"]



# #Option A
# final_answer = generate_answer(query, ranked_docs)

# # Option B (local)
# # final_answer = generate_answer_local(query, retrieved_docs)

# print("Generated Answer:\n", final_answer)
# print(f"The above data is carefully extracted and presented from the paper ids {paper_id_dict}")


