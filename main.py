"""Interface de linha de comando (CLI) para atendimento interativo."""
import sys
from src.agent import AgenteAcademico
from src.config import settings

def main():
    print("=" * 70)
    print("🎓 INSTITUTO HORIZONTE - AGENTE DE ATENDIMENTO ACADÊMICO")
    print("=" * 70)
    print(f"Modelo LLM: {settings.LLM_MODEL}")
    print(f"Provedor: {settings.LLM_PROVIDER}")
    print("Digite sua dúvida acadêmica ou digite 'sair' para encerrar.")
    print("=" * 70)

    try:
        agente = AgenteAcademico()
    except Exception as e:
        print(f"\n❌ Erro ao inicializar o agente: {e}")
        print("Verifique se o arquivo .env contém sua GEMINI_API_KEY configurada corretamente.")
        sys.exit(1)

    while True:
        try:
            pergunta = input("\n👤 Aluno: ").strip()
            if not pergunta:
                continue
            if pergunta.lower() in ["sair", "exit", "quit"]:
                print("\nAtendimento encerrado. Obrigado por utilizar o Instituto Horizonte!")
                break

            print("\n🤖 Processando com LangGraph...")
            saida = agente.processar_mensagem(pergunta)
            resp = saida["resposta_estruturada"]

            print("\n" + "-" * 50)
            print("📋 RESPOSTA AO ALUNO:")
            print(resp.resposta)
            print("-" * 50)
            print(f"📌 Status: {resp.status}")
            print(f"📚 Fontes consultadas: {', '.join(resp.fontes) if resp.fontes else 'Nenhuma'}")
            if resp.protocolo:
                print(f"🎫 Protocolo: {resp.protocolo}")
            if resp.justificativa_decisao:
                print(f"💡 Decisão/Validação: {resp.justificativa_decisao}")
            
            if saida["tool_events"]:
                print(f"🛠️ Ferramentas acionadas ({len(saida['tool_events'])}):")
                for ev in saida["tool_events"]:
                    print(f"   - Tool: {ev['tool']} | Args: {ev['args']}")
            print("-" * 50)

        except KeyboardInterrupt:
            print("\nEncerrando...")
            break
        except Exception as e:
            print(f"\n❌ Erro durante a execução: {e}")

if __name__ == "__main__":
    main()
