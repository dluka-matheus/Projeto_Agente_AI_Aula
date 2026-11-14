# Exemplos de ambientes (infraestrutura, não gabarito)

Estes arquivos mostram como inicializar o backend. Não implementam a avaliação nem substituem o agente RAG/Tools/LangGraph exigido.

## A. Backend local sem Docker

1. Copie `.env.example` para `.env` e configure credenciais de serviços externos.
2. `python -m venv .venv`
3. No PowerShell: `.\.venv\Scripts\Activate.ps1`
4. `pip install -r requirements.txt`
5. `python app/main.py`

## B. Docker Compose apenas para o backend

`docker compose -f compose.backend.yml up --build`

O Compose cria **somente o backend**. Serviços de LLM e vetor podem ficar na nuvem; não há exigência de container adicional.

## C. Docker Compose backend + Qdrant local

`docker compose -f compose.qdrant.yml up --build`

Aqui o Qdrant usa armazenamento persistente; quando executado dentro do container, o backend se conecta a `http://qdrant:6333`, **não** `localhost:6333`.

## Credenciais

- Nunca faça commit do `.env`.
- Use `.env.example` com placeholders.
- Não envie tokens em logs nem prints.
- Nem todo modelo remoto suporta Tool Calling; confira o catálogo e execute um smoke test.

## Observação

O script `app/main.py` é apenas um teste de configuração e rede. O aluno deve implementar seu próprio agente e adaptar as bibliotecas de acordo com o provedor selecionado.
