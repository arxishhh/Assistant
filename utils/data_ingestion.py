import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from pathlib import Path
from uuid import uuid4
from langchain_chroma import Chroma
BASE_DIR = Path('../dataset')

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = Chroma(collection_name= 'FinOps',embedding_function=embeddings,persist_directory= str(Path('../database')))
text_splitter = RecursiveCharacterTextSplitter(separators=[
        "\n\n",
        "\n",
        ". ",
        " "
    ], chunk_size=400, chunk_overlap=100)
for root,dir,file in os.walk(BASE_DIR):
    for f in file:
        print(f'Ingesting data from {f}')
        file_path = os.path.join(BASE_DIR,f)
        loader = PyPDFLoader(file_path)
        split = loader.load_and_split(text_splitter)
        ids = [str(uuid4()) for i in range(len(split))]
        documents = []
        for chunk in split:
            documents.append(Document(page_content=chunk.page_content))
        vector_store.add_documents(documents,ids=ids)
        print(f'Ingested data from {f}')



