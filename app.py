# import os
# import requests
# from bs4 import BeautifulSoup
# import re
# from fpdf import FPDF
# import time
# from urllib.parse import urlparse
#
# # List of 10 safe URLs to scrape (Books to Scrape)
# urls = [
#     "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
#     "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
#     "https://books.toscrape.com/catalogue/category/books/historical-fiction_4/index.html",
#     "https://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html",
#     "https://books.toscrape.com/catalogue/category/books/classics_6/index.html",
#     "https://books.toscrape.com/catalogue/category/books/philosophy_7/index.html",
#     "https://books.toscrape.com/catalogue/category/books/romance_8/index.html",
#     "https://books.toscrape.com/catalogue/category/books/womens-fiction_9/index.html",
#     "https://books.toscrape.com/catalogue/category/books/fiction_10/index.html",
#     "https://books.toscrape.com/catalogue/category/books/nonfiction_13/index.html"
# ]
#
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
# }
#
# # Make sure 'static' folder exists
# if not os.path.exists("static"):
#     os.makedirs("static")
#
# def fetch_webpage(url):
#     response = requests.get(url, headers=headers)
#     response.raise_for_status()
#     return response.text
#
# def parse_html(html_content):
#     soup = BeautifulSoup(html_content, "html.parser")
#     return soup.get_text()
#
# def clean_txt(text):
#     text = " ".join(text.split())
#     text = re.sub(r"http\S+", "", text)
#     text = re.sub(r"[^a-zA-Z0-9\s.,!?\'\"]+", "", text)
#     return text
#
# def write_to_pdf(text_content, output_filename):
#     pdf = FPDF()
#     pdf.set_auto_page_break(auto=True, margin=15)
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#
#     # Split text into chunks to avoid overflowing
#     lines = text_content.split(". ")
#     for line in lines:
#         pdf.multi_cell(0, 10, line.strip() + ".", align="L")
#
#     pdf.output(output_filename)
#
# for idx, url in enumerate(urls, start=1):
#     try:
#         print(f"Fetching page {idx}: {url}")
#         html_content = fetch_webpage(url)
#         page_text = parse_html(html_content)
#         cleaned_text = clean_txt(page_text)
#
#         # Generate safe filename
#         parsed = urlparse(url)
#         parts = parsed.path.rstrip("/").split("/")
#         parent = parts[-2] if len(parts) >= 2 else "index"
#         filename = f"{parent}_{parts[-1]}"
#         output_filename = f"static/{filename}.pdf"
#
#         write_to_pdf(cleaned_text, output_filename)
#         print(f"Saved PDF: {output_filename}")
#
#         # Throttle requests
#         time.sleep(2)
#     except Exception as e:
#         print(f"Error processing {url}: {e}")

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
import google.generativeai as genai
load_dotenv()
import os

from flask import Flask, render_template, request

api_key="AIzaSyCsAJm_lOqye8oSi7DlgXiinoGLEF0Z06I"
genai.configure(api_key=api_key)
# chat history and conversation store will be created once the flask app starts. Chat data will persist as long as the flask session is active.
chat_history = []
conversation_store = {}
FAISS_PATH = "faiss"
llm = GoogleGenerativeAI(model="gemini-1.5-flash")
app = Flask(__name__)
contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""

qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.\

{context}"""

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in conversation_store:
        print(f"Creating store")
        conversation_store[session_id] = ChatMessageHistory()

    return conversation_store[session_id]


def get_document_loader():
    loader = DirectoryLoader('static', glob="**/*.pdf", show_progress=True, loader_cls=PyPDFLoader)
    docs = loader.load()
    return docs


def get_text_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(

        chunk_size=1000,
        chunk_overlap=200,
        length_function=len

    )
    chunks = text_splitter.split_documents(documents)
    return chunks


# ORIGINAL IMPLEMENTATION
# def get_embeddings():
#     documents = get_document_loader()
#     chunks = get_text_chunks(documents)
#     db = FAISS.from_documents(
#         chunks, OpenAIEmbeddings()
#     )

#     return db

# NEW IMPLEMENTATION - Create embeddings and store in a path
def get_embeddings():
    path = os.path.join(os.getcwd(), FAISS_PATH)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    if os.path.exists(path):
        print(f"Index exists. Loading from {path}")
        db = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
    else:
        print(f"Index does not exist. Creating now.")
        documents = get_document_loader()
        chunks = get_text_chunks(documents)
        db = FAISS.from_documents(
            chunks, embeddings
        )
        print(f"Index created. Storing at {path}.")
        db.save_local(path)

    return db



def get_retriever():
    db = get_embeddings()
    retriever = db.as_retriever()
    return retriever


def process_llm_response(chain, question):
    llm_response = chain(question)

    print('Sources:')
    for i, source in enumerate(llm_response['source_documents']):
        result = llm_response['result']
        source_document = source.metadata['source']
        page_number = source.metadata['page']
        print(f"page {page_number}")
        source_document = source_document[7:]

        return result, source_document, page_number


def get_chain():
    retriever = get_retriever()

    chain = RetrievalQA.from_chain_type(llm=llm,
                                        chain_type="stuff",
                                        retriever=retriever,
                                        return_source_documents=True
                                        )
    return chain


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/chat', methods=['GET', 'POST'])
def document_display():
    '''
    If it is a GET request, load the chat page without any values, if it is a POST request read the question in the request, find the answer and render the chat page with the chat history
    '''

    if request.method == 'GET':
        return render_template('chat.html')

    question = request.form['question']
    retriever = get_retriever()

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [("system", contextualize_q_system_prompt), MessagesPlaceholder("chat_history"), ("human", "{input}"), ])
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    qa_prompt = ChatPromptTemplate.from_messages(
        [("system", qa_system_prompt), MessagesPlaceholder("chat_history"), ("human", "{input}"), ])

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    conversational_rag_chain = RunnableWithMessageHistory(rag_chain, get_session_history, input_messages_key="input",
                                                          history_messages_key="chat_history",
                                                          output_messages_key="answer")
    response = conversational_rag_chain.invoke({"input": question}, config={
        "configurable": {"session_id": "abc123"}}, )  # Hardcoding the session_id
    chat_history.append(question)
    chat_history.append(response['answer'])

    return render_template('chat.html', chat_history=chat_history)


if __name__ == "__main__":
    app.run(debug=True)