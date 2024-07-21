import os
import google.generativeai as genai
from uuid import uuid4
from unstructured.partition.pdf import partition_pdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
from dotenv import load_dotenv
from pyfiglet import Figlet
import json
import time
import sys
import logging
from prompt_templates import system_instruction, user_template

def interface():
    os.system("clear")
    figlet = Figlet(font='standard')
    print(figlet.renderText('Silo'))
    print("NOTE: At any point, if you wish to exit, enter X against your query.\n\n")

# a session is a memory of a conversation between user and silo
def initialiseSession():
    session_id = uuid4()
    session = {
        "id": f"{session_id}",
        "conversation": {
                "user": [""],
                "silo": [""]
        }
    }
    return session

# extract text from any PDF
def extractTextFromPDF(filePath: str):
    file = filePath
    elements = partition_pdf(file)

    text = ""
    for element in elements:
        text += f"{str(element)} "
    return text

# Recursive chunking of the text in order to preserve context
def chunkText(text: str):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 256,
        chunk_overlap = 20
    )
    chunks = text_splitter.split_text(text)
    return chunks

# embedding the chunks
def embed(anything: list):
    '''
    sentence-transformer logs everytime it's called but we don't want that
    so we suppress any loggings by it.
    '''
    logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
    model = SentenceTransformer("Supabase/gte-small") # 384 dimensions
    embedding = model.encode(anything)
    logging.getLogger('sentence_transformers').setLevel(logging.INFO)
    return embedding

# indexing the embeddings for search and ranking
def trainIndex(embeddings:list):
    index = faiss.IndexFlatL2(384)
    index.add(embeddings)
    return index

def retrieve(query: list, index: faiss.IndexFlatL2, chunks: list):
    k = 5
    _, indices = index.search(query, k)
    passages = list(chunks[i] for i in indices[0])
    return passages

def printLikeChatGPT(text:str, delay:float):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)

# configure the LLM
def configureGemini():
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=system_instruction,
        generation_config=genai.GenerationConfig(
            max_output_tokens=2000, 
            temperature=0.5)
        )
    return model

def writeSessionToMemory(session: dict):
    with open("session_history.json", "r") as file:
        history = json.load(file)
    history.append(session)

    with open("session_history.json", "w") as file:
        json.dump(history, file, indent=4)

if __name__ == "__main__":
    # using silo: python silo.py /path/to/pdf
    if len(sys.argv) == 2:
        session = initialiseSession()
        filePath = sys.argv[1]
        gemini = configureGemini()
        
        # preprocessing
        interface()
        text = extractTextFromPDF(filePath)
        chunks = chunkText(text)
        embeddings = embed(chunks)
        index = trainIndex(embeddings)
        
        conversation = ""
        while True:
            query = input("USER: ").lower()
            if query != "x":
                query_embed = embed([query])
                passages = retrieve(query_embed, index, chunks)
            
                print("\n")

                conversation += f"user: {session['conversation']['user'][-1]}\nsilo: {session['conversation']['silo'][-1]}\n\n"
                response = gemini.generate_content(user_template.format(
                    query = query, 
                    passages = '\n'.join(passages), 
                    conversation = conversation
                ))
                print("SILO: ", end='')
                printLikeChatGPT(response.text, 0.03)
            
                print("\n")
            
                # append input & output to conversation history:
                session['conversation']['user'].append(query)
                session['conversation']['silo'].append(response.text)
            else:
                break

        writeSessionToMemory(session)
        print("thank you for using silo")

    else:
        sys.exit("Error: No filePath passed as argument.")