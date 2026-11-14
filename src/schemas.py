"""Modelos e contratos tipados com Pydantic para o Agente."""
from typing import List, Optional
from pydantic import BaseModel, Field

class BuscarNormasInput(BaseModel):
    termo_ou_pergunta: str = Field(
        ...,
        description="Termo, dúvida ou palavras-chave para consultar normas e procedimentos acadêmicos oficiais."
    )

class ConsultarProtocoloInput(BaseModel):
    numero_protocolo: str = Field(
        ...,
        description="Identificador único do protocolo no formato SOL-XXXX (exemplo: SOL-1001)."
    )

class RegistrarSolicitacaoInput(BaseModel):
    descricao: str = Field(
        ...,
        description="Descrição clara do que o aluno está solicitando."
    )
    categoria: str = Field(
        ...,
        description="Categoria da solicitação (ex: documentos, certificado, matricula, financeiro, outro)."
    )
    confirmacao_explicita: bool = Field(
        ...,
        description="Deve ser True somente se o usuário pediu ou autorizou explicitamente a abertura do protocolo."
    )

class RespostaAgente(BaseModel):
    """Contrato tipado de saída estruturada do agente acadêmico."""
    resposta: str = Field(
        ...,
        description="Resposta final redigida e humanizada ao aluno."
    )
    fontes: List[str] = Field(
        default_factory=list,
        description="Lista de IDs das normas consultadas (ex: ['ACAD-001']). Vazia se abstido ou não aplicável."
    )
    status: str = Field(
        ...,
        description="Classificação da resposta: 'sucesso', 'abstencao', 'recusa_seguranca', 'protocolo_consultado', 'protocolo_criado', 'erro'."
    )
    protocolo: Optional[str] = Field(
        default=None,
        description="Número do protocolo gerado ou consultado, se houver (ex: 'SOL-1001')."
    )
    justificativa_decisao: Optional[str] = Field(
        default=None,
        description="Justificativa da ação tomada pelo agente ou nó de validação."
    )
