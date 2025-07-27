import streamlit as st
from ranker import retrieve, rerank
from rag import generate_answer 

st.set_page_config(page_title="RAG for The Spiritualist", layout="centered")

st.title("RAG for The Spiritualist")
st.markdown("Ask a question about *The Spiritualist* newspaper archive.")

query = st.text_input("Enter your query", value="Tell me about the THE PSYCHOLOGICAL SOCIETY OF GREAT BRITAIN")

if st.button("Generate Answer"):
    with st.spinner("Retrieving documents..."):
        retrieve_text = retrieve(query, top_k=20)
        ranked_docs = rerank(query, retrieve_text, top_k=5)

    paper_id_dict = {doc["id"]: doc["page_number"] for doc in ranked_docs}

    with st.spinner("Generating answer..."):
        final_answer = generate_answer(query, ranked_docs)

    st.subheader("🔍 Answer")
    st.markdown(final_answer)

    st.subheader("📄 Source Pages")
    for paper_id, page in paper_id_dict.items():
        st.markdown(f"- **Paper ID**: `{paper_id}`, **Page**: `{page}`")


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


