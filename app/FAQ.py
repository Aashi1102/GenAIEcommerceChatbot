import pandas as pd
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from dotenv import load_dotenv
import os 


load_dotenv()

faqs_path = Path(__file__).parent / "app" / "resources" / "faq_data.csv"

Chroma_client = chromadb.Client()
collection_name_faq = "faqs"


Groq_client = Groq()


ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
)

if collection_name_faq in [
    c.name for c in Chroma_client.list_collections()
]:
    Chroma_client.delete_collection(collection_name_faq)

def ingest_faq_data(path):
    if collection_name_faq not in [c.name for c in Chroma_client.list_collections()]:
        print("Ingesting FAQ data...")
        collection = Chroma_client.get_or_create_collection(
            name= collection_name_faq,
            embedding_function=ef
        )


        df = pd.read_csv(path)
        docs = df["question"].tolist()
        metadata = [{"answer": ans} for ans in df["answer"].tolist()]
        ids = [f"id_{i}" for i in range(len(docs))]

        collection.add(
            documents=docs,
            metadatas=metadata,
            ids = ids
        )

        print(f"FAQ Data successfully ingested into Chromadb collection : {collection_name_faq}")
    else:
        print(f"Collection {collection_name_faq} already exists.")      



def get_relevant_faqs(query):
    collection = Chroma_client.get_collection(name=collection_name_faq)
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    return results

# def FAQ_chain(query):
#     relevant_faqs = get_relevant_faqs(query)
#     answers = [item.get("answer") for item in relevant_faqs["metadatas"][0]]
#     context = "\n".join(answers)
#     generated_response = generate_response(query, context)
#     return generated_response


def FAQ_chain(query):
    relevant_faqs = get_relevant_faqs(query)

    documents = relevant_faqs["documents"][0]
    metadatas = relevant_faqs["metadatas"][0]

    # Keep each retrieved question together with its answer
    context_parts = []

    for question, metadata in zip(documents, metadatas):
        answer = metadata.get("answer", "")
        context_parts.append(
            f"Question: {question}\nAnswer: {answer}"
        )

    context = "\n\n".join(context_parts)

    print("User query:", query)
    print("Retrieved FAQ context:\n", context)

    if not context.strip():
        return (
            "I'm sorry, I don't have that information at the moment. "
            "Please contact our support team for further assistance."
        )

    return generate_response(query, context)



def generate_response(query, context):

    
    prompt = f"""
    You are a helpful ecommerce customer support assistant.

    User question:
    {query}

    Retrieved FAQ information:
    {context}

    Instructions:
    1. Answer using only the information in the retrieved FAQs.
    2. Match the user's question with the most relevant FAQ question.
    3. If the FAQs do not contain enough information to answer,
    respond exactly:
    "I'm sorry, I don't have that information at the moment.
    Please contact our support team for further assistance."
    4. Do not invent ecommerce policies or product information.
    5. Keep the answer concise and clear.
    """


    chat_completion = Groq_client.chat.completions.create(
    messages=[
      {
        "role": "user",
        "content": prompt,
      }
    ],
    model = os.environ["GROQ_MODEL_NAME"],

    )

    return chat_completion.choices[0].message.content

    
if __name__ == "__main__":

    ingest_faq_data(faqs_path)
    #result = get_relevant_faqs("How can I reset my password?")
    query = "what's your policy on defective products?"
    answer = FAQ_chain(query)
    print(answer)

