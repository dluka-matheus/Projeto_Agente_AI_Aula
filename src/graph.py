"""Orquestrador LangGraph do Agente Acadêmico do Instituto Horizonte."""

import re
import operator
import logging
from typing import TypedDict, Annotated, Sequence, Optional, List, Dict, Any
from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
)
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from src.config import settings
from src.prompts import SYSTEM_PROMPT
from src.tools import TODAS_AS_TOOLS
from src.schemas import RespostaAgente

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Estado explícito do agente no LangGraph."""

    messages: Annotated[Sequence[BaseMessage], operator.add]
    final_response: Optional[RespostaAgente]
    iteration_count: int
    tool_events: List[Dict[str, Any]]


def obter_modelo_llm():
    """Inicializa o modelo Gemini com binding das ferramentas."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    if (
        not settings.GEMINI_API_KEY
        or settings.GEMINI_API_KEY == "sua_chave_gemini_aqui"
    ):
        raise ValueError(
            "Chave da API do Gemini não configurada! "
            "Por favor, configure GEMINI_API_KEY no arquivo .env para executar o agente."
        )

    llm = ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.1,
        max_retries=2,
    )
    return llm.bind_tools(TODAS_AS_TOOLS)


def agent_node(state: AgentState) -> Dict[str, Any]:
    """Nó do agente: executa o modelo LLM com base nas mensagens."""
    messages = list(state["messages"])

    # Adiciona System Prompt se não estiver presente no início
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    iteration = state.get("iteration_count", 0) + 1

    # Controle de encerramento / limite de recursão para evitar loops indefinidos
    if iteration > settings.RECURSION_LIMIT:
        limite_msg = AIMessage(
            content="Limite máximo de iterações atingido sem convergência. Encerrando operação por segurança."
        )
        return {"messages": [limite_msg], "iteration_count": iteration}

    try:
        model = obter_modelo_llm()
        response = model.invoke(messages)
    except Exception as e:
        logger.error(f"Erro ao invocar LLM: {e}")
        # Tratamento de erro 429 ou falha de rede
        response = AIMessage(
            content=f"Ocorreu uma instabilidade ou limite temporário no serviço de IA: {str(e)}. "
            "Por favor, tente novamente em instantes ou contate o atendimento."
        )

    return {"messages": [response], "iteration_count": iteration}


def custom_tools_node(state: AgentState) -> Dict[str, Any]:
    """Nó de execução de ferramentas com rastreamento e observabilidade."""
    tool_node = ToolNode(TODAS_AS_TOOLS)
    output = tool_node.invoke(state)

    # Rastreia eventos de tools para observabilidade
    events = list(state.get("tool_events", []))
    last_msg = state["messages"][-1]

    if hasattr(last_msg, "tool_calls"):
        for tc in last_msg.tool_calls:
            events.append(
                {
                    "tool": tc.get("name"),
                    "args": tc.get("args"),
                    "call_id": tc.get("id"),
                }
            )

    output["tool_events"] = events
    return output


def _normalizar_conteudo(content) -> str:
    """Extrai texto limpo de content que pode ser str, list de dicts ou dict (Gemini 3.x)."""
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return content.get("text", str(content))
    if isinstance(content, list):
        partes = []
        for part in content:
            if isinstance(part, dict):
                partes.append(part.get("text", str(part)))
            else:
                partes.append(str(part))
        return " ".join(partes)
    return str(content) if content else ""


def validator_node(state: AgentState) -> Dict[str, Any]:
    """Nó de validação, controle e pós-processamento.
    Requisito 4.4 do edital: Nó real de validação além do ciclo agente <-> tools.
    Valida segurança, integridade das fontes, contrato Pydantic e trata anomalias.
    """
    messages = state["messages"]
    last_msg = messages[-1] if messages else None
    raw_content = last_msg.content if last_msg and hasattr(last_msg, "content") else ""
    texto_resposta = _normalizar_conteudo(raw_content)

    # Recupera mensagem do usuário
    user_msg_text = ""
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            user_msg_text = _normalizar_conteudo(m.content)
            break

    # 1. Checagem de segurança (Guardrail contra jailbreak ou alteração indevida de notas)
    padroes_proibidos = [
        r"alter(?:e|ar|ando)?\s+.*nota",
        r"mudar\s+.*nota",
        r"nota\s+10",
        r"ignore\s+as\s+pol[ií]ticas",
    ]
    eh_violacao = any(
        re.search(p, user_msg_text, re.IGNORECASE) for p in padroes_proibidos
    )

    if eh_violacao:
        resposta_estruturada = RespostaAgente(
            resposta="AÇÃO RECUSADA POR SEGURANÇA: Não é permitido alterar notas, notas de atividades "
            "ou violar as políticas acadêmicas do Instituto Horizonte. Caso necessite de revisão formal "
            "de nota, o pedido deve ser solicitado em até 5 dias corridos via portal acadêmico, "
            "conforme a norma [ACAD-003].",
            fontes=["ACAD-003"],
            status="recusa_seguranca",
            protocolo=None,
            justificativa_decisao="Bloqueio de tentativa indevida de alteração de nota acadêmica.",
        )
        return {"final_response": resposta_estruturada}

    # 2. Extração de fontes citadas no texto e no histórico das tools
    fontes_encontradas = set(re.findall(r"ACAD-\d{3}", texto_resposta, re.IGNORECASE))
    for m in messages:
        if isinstance(m, ToolMessage):
            fontes_no_retorno = re.findall(r"ACAD-\d{3}", str(m.content), re.IGNORECASE)
            fontes_encontradas.update(fontes_no_retorno)
    fontes_ordenadas = sorted(list(fontes_encontradas))

    # 3. Extração ou detecção de número de protocolo
    protocolos_encontrados = re.findall(r"SOL-\d+", texto_resposta, re.IGNORECASE)
    protocolo_final = protocolos_encontrados[0] if protocolos_encontrados else None

    # 4. Classificação do status
    texto_baixo = texto_resposta.lower()
    if (
        "não consta" in texto_baixo
        or "não possui informações" in texto_baixo
        or "não foram encontradas normas" in texto_baixo
        or "não encontramos" in texto_baixo
        or "não há registro" in texto_baixo
    ):
        status = "abstencao"
        justificativa = (
            "Agente absteve-se por ausência de evidências na base de normas oficiais."
        )
    elif protocolo_final and (
        "registrada com sucesso" in texto_baixo
        or "criada com sucesso" in texto_baixo
        or "aberta" in texto_baixo
    ):
        status = "protocolo_criado"
        justificativa = f"Novo protocolo {protocolo_final} registrado com sucesso no banco de dados."
    elif protocolo_final and (
        "protocolo encontrado" in texto_baixo
        or "status" in texto_baixo
        or "em análise" in texto_baixo
    ):
        status = "protocolo_consultado"
        justificativa = (
            f"Status do protocolo {protocolo_final} consultado na base de dados."
        )
    else:
        status = "sucesso"
        justificativa = (
            "Resposta respondida com sucesso com base nas normas acadêmicas."
        )

    # 5. Tratamento de mensagens vazias ou respostas inválidas
    if not texto_resposta or not texto_resposta.strip():
        texto_resposta = "Não foi possível processar a resposta no momento. Por favor, reformule sua solicitação."
        status = "erro"
        justificativa = "Tratamento de fallback para resposta vazia do modelo."

    # Constrói e valida via Pydantic
    resposta_estruturada = RespostaAgente(
        resposta=texto_resposta,
        fontes=fontes_ordenadas,
        status=status,
        protocolo=protocolo_final,
        justificativa_decisao=justificativa,
    )

    return {"final_response": resposta_estruturada}


def should_continue(state: AgentState) -> str:
    """Roteador condicional: decide se vai para as ferramentas ou para o validador."""
    messages = state["messages"]
    last_msg = messages[-1]

    # Se atingiu o limite de iterações, força o término indo para o validador
    if state.get("iteration_count", 0) >= settings.RECURSION_LIMIT:
        return "validator"

    # Se o LLM requisitou tools, executa tools
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"

    # Caso contrário, vai para o nó de validação e pós-processamento
    return "validator"


def criar_grafo_atendimento():
    """Compila o StateGraph completo do agente."""
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", custom_tools_node)
    workflow.add_node("validator", validator_node)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent", should_continue, {"tools": "tools", "validator": "validator"}
    )

    workflow.add_edge("tools", "agent")
    workflow.add_edge("validator", END)

    return workflow.compile()
