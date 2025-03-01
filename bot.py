from dotenv import load_dotenv
import os
import openai

os.environ['OPENAI_API_KEY'] = '<YOUR_OPENAPI_KEY>'


load_dotenv()

API_KEY = os.environ.get("API_KEY")

"""## 3: Loading your custom data
To use data with an LLM, documents must first be loaded into a vector database.
The first step is to load them into memory via a loader
"""

from langchain.document_loaders import TextLoader , UnstructuredExcelLoader


loader = UnstructuredExcelLoader(
    "./sample_data/customDataOnExcel.xlsx"
)
docs = loader.load()

"""### Text splitter
Split the loaded data and put it in chunks to the vector db
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=500,
)

documents = text_splitter.split_documents(docs)
# documents

"""## Embeddings
Texts are not stored as text in the database, but as vector representations.
Embeddings are a type of word representation that represents the semantic meaning of words in a vector space.
"""

from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(openai_api_key=API_KEY)

"""## Loading Vectors into VectorDB (FAISS)
As created by OpenAIEmbeddings vectors can now be stored in the database. The DB can be stored as .pkl file
"""

from langchain.vectorstores.faiss import FAISS
import pickle

vectorstore = FAISS.from_documents(documents, embeddings)

with open("vectorstore.pkl", "wb") as f:
    pickle.dump(vectorstore, f)

"""## Loading the database
Before using the database, it must of course be loaded again.
"""

with open("vectorstore.pkl", "rb") as f:
    vectorstore = pickle.load(f)

"""## Prompts
With an LLM you have the possibility to give it an identity before a conversation or to define how question and answer should look like.
"""

from langchain.prompts import PromptTemplate


basePrompt = """
    Put your prompt here
    {context}
    Question: {question}
    Answer here:
  """

PROMPT = PromptTemplate(
    template=basePrompt, input_variables=["context", "question"]
)

"""## Chains
With chain classes you can easily influence the behavior of the LLM
"""

from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

chain_type_kwargs = {"prompt": PROMPT}

llm = OpenAI(openai_api_key=API_KEY)

"""## Memory
"""

from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True, output_key="answer"
)

"""## Using Memory in Chains
"""

from langchain.chains import ConversationalRetrievalChain
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

qa = ConversationalRetrievalChain.from_llm(
    llm=OpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=API_KEY),
    memory=memory,
    retriever=vectorstore.as_retriever(),
    combine_docs_chain_kwargs={"prompt": PROMPT},
)

"""# Python Web Server"""

from flask import Flask, render_template, render_template_string, request, jsonify
from flask_ngrok import run_with_ngrok

# ===== Web Server with NgRok ===
app = Flask(__name__)
run_with_ngrok(app)

# Once the application is runs successfully you can call the API inside your chatbot 

@app.route('/submit-prompt', methods=['POST'])
def generate():

    data = request.get_json()
    prompt = data.get('prompt', '')

    query = prompt
    print("Question Asked: ", query);

    response = qa({"question": query})

    print("Sending Response...")
    data = {
        "response": response["answer"]
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run()