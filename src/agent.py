"""Interface do Agente Acadêmico do Instituto Horizonte."""
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage
from src.graph import criar_grafo_atendimento
from src.schemas import RespostaAgente

class AgenteAcademico:
    def __init__(self):
        self.app = criar_grafo_atendimento()

    def processar_mensagem(self, mensagem_usuario: str) -> Dict[str, Any]:
        """Processa a mensagem do aluno e retorna a resposta estruturada com metadados de execução."""
        estado_inicial = {
            "messages": [HumanMessage(content=mensagem_usuario)],
            "final_response": None,
            "iteration_count": 0,
            "tool_events": []
        }

        resultado = self.app.invoke(estado_inicial)
        
        resposta_final: RespostaAgente = resultado.get("final_response")
        eventos_tools: List[Dict[str, Any]] = resultado.get("tool_events", [])
        
        return {
            "resposta_estruturada": resposta_final,
            "tool_events": eventos_tools,
            "total_iteracoes": resultado.get("iteration_count", 0),
            "historico_mensagens": resultado.get("messages", [])
        }
