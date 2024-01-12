import uuid
from openai import AzureOpenAI
from extract_from_pdf import chunk_texts, extract_texts
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient  
from azure.search.documents.indexes import SearchIndexClient  
from azure.search.documents.indexes.models import (  
    SearchIndex,  
    SearchField,  
    SearchFieldDataType,  
    SimpleField,  
    SearchableField,   
    VectorSearch,
    HnswVectorSearchAlgorithmConfiguration,  
)

load_dotenv()

openai_embedding_mode_deployment_name = os.environ.get("AZURE_OPENAI_EMB_DEPLOYMENT")
openai_client = AzureOpenAI(azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
                            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                            api_version="2023-05-15")

search_service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT") 
search_service_admin_key = os.environ.get("AZURE_SEARCH_ADMIN_KEY")
credential = AzureKeyCredential(search_service_admin_key)

index_name = "balance-sheet-index"

# Create a search index
index_client = SearchIndexClient(
    endpoint=search_service_endpoint, credential=credential)
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
    SearchableField(name="fundRow", type=SearchFieldDataType.String, filterable=True),
    SearchField(name="fundRowVector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True, vector_search_dimensions=1536, vector_search_configuration="my-vector-config")
]

vector_search = VectorSearch(
    algorithm_configurations=[
        HnswVectorSearchAlgorithmConfiguration(
            name="my-vector-config",
            kind="hnsw",
            parameters={
                "m": 4,
                "efConstruction": 400,
                "efSearch": 500,
                "metric": "cosine"
            }
        )
    ]
)

# Create the search index with the semantic settings
index = SearchIndex(name=index_name, fields=fields,
                    vector_search=vector_search)
result = index_client.create_or_update_index(index)
print(f' {result.name} created')

azcs_search_client = SearchClient(search_service_endpoint, index_name=index_name, credential=credential)


def generate_embeddings(text):
    response = openai_client.embeddings.create(input=text,
                                               model=openai_embedding_mode_deployment_name)
    embeddings = response.data[0].embedding
    return embeddings


def add_or_update(document):
    azcs_search_client.merge_or_upload_documents(documents=document)

# Example usage:
pdf_data = open('Sample Financials Data - Balance Sheet (1).pdf', 'rb').read()
extracted_texts = extract_texts(pdf_data)
chunked_texts = chunk_texts(extracted_texts)

# Process and store all the chunked texts
chunk_documents = []
for chunk_text in chunked_texts:
    chunk_embeddings = generate_embeddings(chunk_text)
    chunk_document = {
        "id": str(uuid.uuid4()),
        "fundRow": chunk_text,
        "fundRowVector": chunk_embeddings
    }
    chunk_documents.append(chunk_document)

# Call add_or_update only once after processing all chunks
add_or_update(chunk_documents)
