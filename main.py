import os
import cerebro

# ============================================================
# JARVIS IA — Ponto de Entrada Principal
# ============================================================

VERSAO = "1.0.0"

BANNER = f"""
╔══════════════════════════════════════════════════╗
║          ⚡  J.A.R.V.I.S.  v{VERSAO}  ⚡           ║
║   Just A Rather Very Intelligent System          ║
╠══════════════════════════════════════════════════╣
║  Assistente IA pessoal · Linux Pop!_OS           ║
║  LLM Local via Ollama · Acesso total ao sistema  ║
╚══════════════════════════════════════════════════╝
"""

if __name__ == "__main__":
    os.system("clear")
    print(BANNER)
    print("🤖 Jarvis: Bom dia, senhor. Todos os sistemas operacionais.")
    print("   Digite 'sair' para encerrar a sessão.\n")

    while True:
        try:
            txt = input("👤 Você: ").strip()

            if not txt:
                continue
            if txt.lower() in ['sair', 'tchau', 'encerrar', 'quit', 'exit']:
                print("\n🤖 Jarvis: Até logo, senhor. Estarei aqui quando precisar.")
                break

            resposta = cerebro.pensar_e_agir(txt)
            print(resposta)

        except KeyboardInterrupt:
            print("\n\n🤖 Jarvis: Sessão encerrada. Até breve, senhor.")
            break