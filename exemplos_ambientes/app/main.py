"""Exemplo de boot de backend: NÃO implementa o trabalho final."""
import os
from dotenv import load_dotenv
load_dotenv()
print('Backend iniciado')
print('LLM provider:', os.getenv('LLM_PROVIDER', 'não configurado'))
print('Vector provider:', os.getenv('VECTOR_PROVIDER', 'não configurado'))
print('Vector endpoint:', os.getenv('VECTOR_ENDPOINT', 'integrado / não informado'))
# TODO: criar config, LLM, embeddings, retriever, Tools e StateGraph
