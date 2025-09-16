from openai import OpenAI
import json

# Initialize client with custom base URL and no API key
client = OpenAI(base_url="http://10.6.125.217:8080/v1", api_key='')

# Chat completions example
chat_response = client.chat.completions.create(
    model="qwen/qwen3-14b",
    messages=[
        {"role": "system", "content": "Always answer in rhymes."},
        {"role": "user", "content": "Introduce yourself."}
    ],
    temperature=0.7,
    max_tokens=-1,
)

print(chat_response.choices)

# Embeddings example
embed_response = client.embeddings.create(
    model="text-embedding-nomic-embed-text-v2-moe",
    input=[
        "Embed this string for me!",
        "Also embed this one!"
    ]
)

print("\nEmbeddings response:")
print(embed_response)