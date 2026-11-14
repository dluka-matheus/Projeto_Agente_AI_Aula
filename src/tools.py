"""Ferramentas (Tools) LangChain tipadas para o Agente."""
import re
import json
from langchain_core.tools import tool
from src.schemas import BuscarNormasInput, ConsultarProtocoloInput, RegistrarSolicitacaoInput
from src.rag import rag_manager
from src.database import consultar_protocolo_db, registrar_solicitacao_db

@tool(args_schema=BuscarNormasInput)
def buscar_normas(termo_ou_pergunta: str) -> str:
    """Consulta as normas, regulamentos e procedimentos oficiais do Instituto Horizonte.
    Use sempre que o aluno fizer perguntas sobre prazos, frequência, notas, certificados,
    segurança, biblioteca, trancamento ou regras institucionais.
    """
    if not termo_ou_pergunta or not termo_ou_pergunta.strip():
        return "Erro: O termo ou pergunta para busca de normas não pode ser vazio."

    docs = rag_manager.buscar(termo_ou_pergunta)
    if not docs:
        return "Nenhuma norma oficial foi encontrada para o termo pesquisado."

    resultado = ["DOCUMENTOS E NORMAS OFICIAIS ENCONTRADAS:"]
    for i, doc in enumerate(docs, 1):
        resultado.append(
            f"\n--- Documento [{doc['fonte']}] ({doc['categoria']}) ---\n"
            f"{doc['conteudo']}"
        )
    return "\n".join(resultado)

@tool(args_schema=ConsultarProtocoloInput)
def consultar_protocolo(numero_protocolo: str) -> str:
    """Consulta o status e o histórico de uma solicitação ou protocolo acadêmico existente (ex: SOL-1001).
    Não invente status nem números de protocolo inexistentes.
    """
    num = numero_protocolo.strip().upper()
    if not re.match(r"^SOL-\d+$", num):
        return f"Formato de protocolo inválido: '{numero_protocolo}'. O formato oficial deve ser SOL-XXXX (ex: SOL-1001)."

    dados = consultar_protocolo_db(num)
    if not dados:
        return f"O protocolo '{num}' não foi localizado na base de dados acadêmica. Verifique o número digitado."

    return (
        f"PROTOCOLO ENCONTRADO:\n"
        f"- Número: {dados['numero']}\n"
        f"- Categoria: {dados['categoria']}\n"
        f"- Descrição: {dados['descricao']}\n"
        f"- Status Atual: {dados['status']}\n"
        f"- Data de Criação: {dados['criado_em']}\n"
        f"- Última Atualização: {dados['atualizado_em']}"
    )

@tool(args_schema=RegistrarSolicitacaoInput)
def registrar_solicitacao(descricao: str, categoria: str, confirmacao_explicita: bool = False) -> str:
    """Registra uma nova solicitação formal na secretaria acadêmica do Instituto Horizonte.
    ATENÇÃO: Requer intenção explícita do aluno (confirmacao_explicita=True).
    Esta ferramenta NÃO pode ser usada para alterar notas ou violar regras institucionais.
    """
    desc_limpa = descricao.strip().lower()

    # Guardrail de segurança: impedir alteração indevida de notas ou ações fraudulentas
    termos_proibidos = ["alterar nota", "mudar nota", "aumentar nota", "nota 10", "fraude", "burlar"]
    if any(termo in desc_limpa for termo in termos_proibidos):
        return (
            "AÇÃO RECUSADA POR SEGURANÇA: O sistema acadêmico não permite o registro de "
            "solicitações para alteração direta de notas ou violação de políticas institucionais."
        )

    if not confirmacao_explicita:
        return (
            "CONFIRMAÇÃO NECESSÁRIA: A abertura de nova solicitação acadêmica requer intenção "
            "e autorização explícita do usuário. Por favor, confirme se deseja abrir este chamado formalmente."
        )

    novo_protocolo = registrar_solicitacao_db(descricao=descricao, categoria=categoria)
    return (
        f"SOLICITAÇÃO REGISTRADA COM SUCESSO!\n"
        f"- Número do Protocolo: {novo_protocolo['numero']}\n"
        f"- Categoria: {novo_protocolo['categoria']}\n"
        f"- Descrição: {novo_protocolo['descricao']}\n"
        f"- Status: {novo_protocolo['status']}\n"
        f"- Data de Registro: {novo_protocolo['criado_em']}"
    )

TODAS_AS_TOOLS = [buscar_normas, consultar_protocolo, registrar_solicitacao]
