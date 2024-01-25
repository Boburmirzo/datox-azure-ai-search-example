import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient  
from azure.search.documents.models import Vector

load_dotenv()

openai_embedding_model_deployment_name = os.environ.get("AZURE_OPENAI_EMB_DEPLOYMENT")
openai_gpt_model_deployment_name = os.environ.get("AZURE_OPENAI_GPT_DEPLOYMENT")
openai_client = AzureOpenAI(azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
                            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                            api_version="2023-05-15")

search_service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT") 
search_service_admin_key = os.environ.get("AZURE_SEARCH_ADMIN_KEY")
credential = AzureKeyCredential(search_service_admin_key)

index_name = "balance-sheet-index-v2"

azcs_search_client = SearchClient(
    endpoint=search_service_endpoint, index_name=index_name, credential=credential)


def generate_embeddings(search_text):
    response = openai_client.embeddings.create(input=search_text, 
                                               model=openai_embedding_model_deployment_name)
    embeddings = response.data[0].embedding
    return embeddings


def search_knowledgebase(search_query):
    vector = Vector(value=generate_embeddings(search_query), k=3, fields="fundRowVector")
    print("search query: ", search_query)
    results = azcs_search_client.search(  
        search_text=search_query,  
        vectors=[vector],
        select=["fundRow"],
        top=1
    )  
    text_content = ""
    for result in results:
        text_content += f"{result['fundRow']}"
    return text_content


fund_name = "Alpha FND"
text_content = search_knowledgebase(fund_name)
print(text_content)

system_content = f"You are an AI assistant that extracts the data from the financial document for fund '{fund_name}'"
user_content = f"Convert the following data data: '{text_content}' into a structured JSON and return only JSON in the response"

print(system_content)

response = openai_client.chat.completions.create(
    model=openai_gpt_model_deployment_name, 
    messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
    ])

print("*************************Result**************************")
print(response.choices[0].message.content)