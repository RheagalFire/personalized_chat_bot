import pinecone
import os

PINECONE_KEY = os.getenv('PINECONE_KEY')

# initialize connection to pinecone
pinecone.init(
    api_key=PINECONE_KEY,
    environment="eu-west1-gcp"
)

index_name = 'personalized-bot'
index = pinecone.Index(index_name)

# Your query logic goes here
# For example:
stats = index.describe_index_stats()
print(stats)
