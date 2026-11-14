# Como escolher o ambiente (consulta em 04/11/2026)

**Regra**: apenas o backend precisa ser executável e verificável por testes. Docker Compose é opcional. O LLM e o banco vetorial podem ser locais ou em cloud. Não há desconto na nota por essa escolha.

## Recomendações por limitação de hardware

- **Notebook simples**: Python direto + Gemini API (free quando elegível) + Pinecone Starter com índice/embeddings gerenciados.
- **Sem cartão / cota LLM apertada**: Python direto + Groq Free ou OpenRouter :free + Qdrant Cloud Free; confirmar suporte a Tools.
- **Já domina Docker**: compose apenas backend + banco vetorial e LLM em cloud.
- **Quer aprender redes entre containers**: compose backend + Qdrant; LLM em cloud.
- **Prefere tudo local**: Ollama/LocalAI e Chroma/LanceDB, se o hardware suportar.

## Provedores de LLM (gratuito não é ilimitado)

| Serviço | Acesso | Cuidado |
|---|---|---|
| Google Gemini API | Alguns modelos com tier sem custo | Elegibilidade, quotas, Tool Calling por modelo. https://ai.google.dev/gemini-api/docs/pricing |
| GroqCloud | Free tier com limites | Consultar limites por modelo. https://console.groq.com/docs/rate-limits |
| OpenRouter | Modelos `:free`, 50 req/dia no plano Free consultado | Modelo e suporte a Tools variam. https://openrouter.ai/pricing |
| Cloudflare Workers AI | Franquia free de 10 mil neurons/dia consultada | Alguns modelos exigem plano pago. https://developers.cloudflare.com/workers-ai/platform/pricing/ |
| Hugging Face Inference Providers | Crédito Free ~US$ 0,10/mês na consulta | Muito limitado. https://huggingface.co/docs/inference-providers/pricing |
| Ollama / LocalAI | Software local | Modelo pesa na máquina; selecionar modelos pequenos com suporte a Tools. https://ollama.com/download |

## Vector stores (gratuitos ou executados localmente)

| Serviço | Tipo | Cuidados |
|---|---|---|
| Pinecone Starter | Cloud grátis com limites | Confirme inclusão de inferência e cotas. https://www.pinecone.io/pricing/ |
| Qdrant Cloud Free | Cloud grátis para protótipos | Pode suspender por inatividade. https://qdrant.tech/documentation/cloud/create-cluster/ |
| Supabase Free + pgvector | Cloud Postgres com 500 MB | Pode pausar por inatividade. https://supabase.com/pricing |
| Chroma / LanceDB | Embedded local | Sem servidor cloud nem conta obrigatória. https://lance.org/quickstart/lancedb/ |
| Qdrant local | Docker | Leva consumo de RAM/armazenamento local. https://qdrant.tech/documentation/quickstart/ |

## Quando o limite acabar

Salve logs/traces verdadeiros com segredos mascarados e os resultados dos cenários de teste enquanto o serviço funciona. Não é necessário gravar vídeo. Trate 429 e timeouts no código. Mocks ajudam testes, mas não substituem evidência de retrieval/Tool Calling reais.
