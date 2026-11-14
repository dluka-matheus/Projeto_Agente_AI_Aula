# Instituto Horizonte — Agente Inteligente de Atendimento Acadêmico
**Avaliação Integradora — Aplicações Avançadas de IA (PEW1029)**  
Pós-graduação | Turma 6001 | 2026.2

---

## 1. Visão Geral da Arquitetura
O sistema implementa um **Agente Inteligente de Atendimento Acadêmico** para o Instituto Horizonte, desenvolvido com **LangChain**, **LangGraph** e **ChromaDB**, utilizando a API do **Google Gemini** (`gemini-1.5-flash`).

### Destaques do Projeto:
- **Prompt & Saída Estruturada (Pydantic):** Validação tipada (`RespostaAgente`), garantindo contrato consistente contendo `resposta`, `fontes`, `status`, `protocolo` e `justificativa_decisao`.
- **RAG & Recuperação de Normas:** Indexação completa dos documentos normativos oficiais (`ACAD-001` a `ACAD-012`) com metadados e busca com Top-K configurável via ChromaDB.
- **Tools Tipadas:**
  1. `buscar_normas`: Recuperação semântica de regras e procedimentos oficiais.
  2. `consultar_protocolo`: Consulta determinística a protocolos simulados existentes (ex: `SOL-1001`) sem inventar dados.
  3. `registrar_solicitacao`: Tool de ação que valida intenção explícita e persiste novo protocolo em banco SQLite real (`protocolos.db`).
- **Orquestração LangGraph:** `StateGraph` explícito com nó do agente, nó de ferramentas, roteador condicional e um **nó de validação / controle / pós-processamento** (`validator_node`) que atua como guardrail ético, sanitizador e validador de contrato Pydantic.
- **Prevenção de Loops:** Controle explícito de recursão (`recursion_limit`).
- **Bônus SDD (+0,5):** Arquitetura documentada no fluxo *Intent → Spec → Plan → Tasks → Implement/Test/Validate* no arquivo `SPEC_DRIVEN_DEVELOPMENT.md`.

---

## 2. Estrutura do Repositório

```text
Avaliacao_IA/
├── base_conhecimento_academica.json   # 12 documentos oficiais simulados
├── cenarios_de_teste_aluno.csv         # 10 cenários de teste oficiais
├── DOCUMENTOS_FICTICIOS_ACADEMICOS/   # Fontes complementares em Markdown/Docx
├── src/
│   ├── __init__.py
│   ├── config.py                      # Configurações e leitura do .env
│   ├── schemas.py                     # Contratos Pydantic (Structured Output)
│   ├── database.py                   # Persistência SQLite de protocolos
│   ├── rag.py                        # Vector Store Chroma & Ingestão RAG
│   ├── tools.py                      # 3 Tools tipadas (buscar, consultar, registrar)
│   ├── prompts.py                    # System prompt e regras institucionais
│   ├── graph.py                      # StateGraph do LangGraph e Nó de Validação
│   └── agent.py                      # Interface unificada do agente
├── main.py                            # CLI interativa para atendimento ao vivo
├── testes_cenarios.py                 # Bateria automatizada dos 10 cenários
├── relatorio_testes.md                # Relatório com evidências dos testes
├── SPEC_DRIVEN_DEVELOPMENT.md         # Documentação da metodologia SDD (bônus)
├── requirements.txt                   # Dependências do projeto
├── .env.example                       # Exemplo de configuração sem credenciais
└── README.md                          # Este documento
```

---

## 3. Modo de Execução Escolhido
**Modalidade A / D (Backend local em Python sem Docker com LLM em nuvem)**:
- **Backend:** Python 3.11+ executando localmente.
- **LLM:** Google Gemini API (`gemini-1.5-flash`).
- **Embeddings:** `models/text-embedding-004` (ou fallback local).
- **Vector DB:** ChromaDB (embutido localmente, sem necessidade de servidores externos).
- **Banco Relacional:** SQLite embutido (`protocolos.db`).

---

## 4. Guia Rápido de Instalação e Execução

### Passo 1: Clonar/Acessar a Pasta do Projeto
Abra o terminal no diretório do projeto:
```powershell
cd c:\Users\dluka\OneDrive\Documentos\Avaliacao_IA\Avaliacao_IA
```

### Passo 2: Criar e Ativar o Ambiente Virtual
```powershell
# Criação do ambiente virtual
python -m venv .venv

# Ativação no Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### Passo 3: Instalar as Dependências
```powershell
pip install -r requirements.txt
```

### Passo 4: Configurar as Credenciais (.env)
Copie o arquivo `.env.example` para `.env` (se ainda não existir):
```powershell
Copy-Item .env.example .env
```
Edite o arquivo `.env` e configure sua chave da API do Google Gemini:
```env
GEMINI_API_KEY=AIzaSy...sua_chave_aqui
LLM_MODEL=gemini-1.5-flash
```

---

## 5. Como Executar

### 5.1. Atendimento Interativo (CLI)
Para conversar interativamente com o assistente:
```powershell
python main.py
```

### 5.2. Executar a Suíte dos 10 Cenários de Teste
Para rodar a validação automática oficial e gerar o relatório com evidências:
```powershell
python testes_cenarios.py
```
Isso gerará os arquivos:
- `relatorio_testes.md`: Relatório completo formatado com justificativas e evidências.
- `relatorio_testes.json`: Estrutura de dados com o trace das execuções.

---

## 6. Declaração de Uso de IA e Decisões Técnicas (Seção 5 do Edital)

1. **IAs que auxiliaram no desenvolvimento:**
   - **Google Gemini / Antigravity AI:** Auxílio no planejamento arquitetural, estruturação das tipagens Pydantic, nós do LangGraph e geração dos testes automatizados.
2. **Duas Decisões Técnicas Revisadas pelo Estudante:**
   - **Decisão 1 — Utilização de ChromaDB Local Persistente:** Foi priorizado o uso do ChromaDB embutido em detrimento de provedores de nuvem que desativam clusters por inatividade (como Qdrant Cloud ou Pinecone Starter), garantindo total reprodutibilidade pelo avaliador sem risco de indisponibilidade externa.
   - **Decisão 2 — Nó Dedicado de Validação e Segurança no LangGraph:** Implementação de um nó posterior (`validator_node`) encarregado de validar o schema Pydantic, inspecionar intenções maliciosas (tentativas de alteração de nota como no cenário T10) e assegurar a extração de fontes das ferramentas, desacoplando a lógica de guardrail do ciclo do LLM.
