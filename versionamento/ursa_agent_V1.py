import os
import json
import pyautogui
from openai import OpenAI
from datetime import datetime

# --- Configuração do Cérebro ---
client = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

# --- As Mãos (Funções Reais) ---
def abrir_programa(nome_programa):
    """Abre um programa no Linux usando o terminal"""
    programas = {
        "calculadora": "gnome-calculator",
        "navegador": "firefox",
        "arquivos": "nautilus",
        "vscode": "code",
        "terminal": "gnome-terminal"
    }
    
    cmd = programas.get(nome_programa.lower())
    if cmd:
        os.popen(cmd) # Executa o comando no terminal
        return f"Sucesso: O programa {nome_programa} foi aberto."
    else:
        return f"Erro: Não sei abrir o programa '{nome_programa}'. Tente: calculadora, navegador, vscode."

def pegar_hora():
    return datetime.now().strftime("%H:%M")

# --- O Maestro (Cérebro + Mãos) ---
def processar_comando(usuario_input):
    # 1. Instrução para a IA saber que ela tem mãos
    sistema = """
    Você é a Ursa, uma Assistente Desktop no Pop!_OS.
    VOCÊ TEM ACESSO A FERRAMENTAS. Se o usuário pedir algo que exija uma ação,
    você DEVE responder APENAS um JSON (sem texto extra) no formato:
    { "funcao": "nome_da_funcao", "parametro": "valor" }

    Funções disponíveis:
    - abrir_programa(nome_programa): Use para abrir apps (calculadora, vscode, navegador).
    - pegar_hora(): Use quando perguntarem as horas.
    
    Se for apenas papo furado, responda um JSON com:
    { "funcao": "responder", "parametro": "Sua resposta sarcástica aqui" }
    """

    # 2. Pergunta pro Llama (Forçando resposta em JSON)
    print("🐻 Pensando...", end="\r")
    response = client.chat.completions.create(
        model="llama3",
        messages=[
            {"role": "system", "content": sistema},
            {"role": "user", "content": usuario_input}
        ],
        response_format={"type": "json_object"}, # O Pulo do gato! Garante JSON.
        temperature=0.1 # Criatividade baixa para não errar o código
    )

    resposta_raw = response.choices[0].message.content
    
    try:
        # 3. Decodifica o JSON da IA
        acao = json.loads(resposta_raw)
        funcao = acao.get("funcao")
        param = acao.get("parametro")

        # 4. Executa a ação real
        if funcao == "abrir_programa":
            resultado = abrir_programa(param)
            return f"✅ {resultado}"
        
        elif funcao == "pegar_hora":
            hora = pegar_hora()
            return f"⏰ São exatamente {hora}, Otávio."
            
        elif funcao == "responder":
            return f"🐻 Ursa: {param}"
            
    except Exception as e:
        return f"bugou: {e} | A IA tentou: {resposta_raw}"

# --- Loop Principal ---
if __name__ == "__main__":
    print("🤖 SISTEMA URSA V1 (COM FUNÇÕES) INICIADO")
    print("Tente: 'Abra a calculadora' ou 'Que horas são?'")
    
    while True:
        txt = input("\n👨‍💻 Você: ")
        if txt.lower() in ['sair', 'tchau']: break
        
        resposta = processar_comando(txt)
        print(resposta)