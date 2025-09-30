from openai import OpenAI
import streamlit as st
import json

client = OpenAI(base_url=st.secrets.base_url, api_key='')

# Chat completions example
chat_response = client.chat.completions.create(
    model=st.secrets.model,
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
    model=st.secrets.embedding_model,
    input=[
        "Embed this string for me!",
        "Also embed this one!"
    ]
)

print("\nEmbeddings response:")
print(embed_response)