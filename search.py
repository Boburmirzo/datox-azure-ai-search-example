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

index_name = "balance-sheet-index"

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
        select=["fundRow","fundtitle"]
    )  
    text_content = ""
    for result in results: 
        print(result) 
        text_content += f"{result['fundtitle']}:{result['fundRow']}"
    print("text_content", text_content)
    return text_content

search_query = "Show assets of ALPHA FND"
text_content = search_knowledgebase(search_query)
prompt = f"Given assets of ALPHA FND: {text_content}, show only total assets value with date without explanation"
response = openai_client.completions.create(model=openai_gpt_model_deployment_name, prompt=prompt, max_tokens=200)

print("*************************Result**************************")
print(response)