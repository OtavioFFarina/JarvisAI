import os
import json
import subprocess
import shutil
from openai import OpenAI
from datetime import datetime

# --- Configuração do Cérebro ---
client = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

# --- FERRAMENTAS DO SISTEMA (OS BRAÇOS) ---

def abrir_programa(nome_programa):
    """Tenta abrir programas de forma inteligente"""
    nome = nome_programa.lower().strip()
    
    # Mapa de sinônimos -> Comandos possíveis
    mapa = {
        "navegador": ["brave-browser", "brave", "google-chrome", "firefox"],
        "brave": ["brave-browser", "brave-browser-stable", "flatpak run com.brave.Browser"],
        "vscode": ["code", "flatpak run com.visualstudio.code"],
        "calculadora": ["gnome-calculator", "flatpak run org.gnome.Calculator"],
        "terminal": ["gnome-terminal", "konsole"]
    }
    
    comandos_tentar = mapa.get(nome, [nome]) # Se não achar no mapa, tenta o nome cru
    
    for cmd in comandos_tentar:
        # shutil.which verifica se o comando existe no sistema antes de tentar rodar
        # Se for flatpak (tem espaço), a gente pula a verificação do shutil e tenta direto
        if " " in cmd or shutil.which(cmd):
            print(f"DEBUG: Tentando executar: {cmd}")
            os.system(f"{cmd} > /dev/null 2>&1 &")
            return f"✅ Tentei abrir '{nome}' usando o comando: {cmd}"
            
    return f"❌ Erro: Não encontrei o programa '{nome}' instalado no sistema."

def criar_projeto(nome_projeto, tipo):
    """Cria uma pasta e um arquivo inicial básico"""
    base_path = os.path.expanduser("~/Projetos") # Cria na pasta Projetos do seu usuário
    caminho_projeto = os.path.join(base_path, nome_projeto)
    
    try:
        # 1. Cria a pasta
        if not os.path.exists(caminho_projeto):
            os.makedirs(caminho_projeto)
        
        mensagem = f"Pasta criada em {caminho_projeto}. "
        
        # 2. Cria arquivo inicial baseado no tipo
        arquivo_init = ""
        conteudo = ""
        
        if "python" in tipo.lower():
            arquivo_init = "main.py"
            conteudo = "print('Hello World - Criado pela Ursa 🐻')\n"
        elif "web" in tipo.lower() or "html" in tipo.lower():
            arquivo_init = "index.html"
            conteudo = "<h1>Hello World - Ursa 🐻</h1>"
        elif "texto" in tipo.lower():
            arquivo_init = "notas.txt"
            conteudo = "Projeto iniciado pela Ursa."
            
        if arquivo_init:
            caminho_arq = os.path.join(caminho_projeto, arquivo_init)
            with open(caminho_arq, "w") as f:
                f.write(conteudo)
            mensagem += f"Arquivo {arquivo_init} criado."
            
            # Bônus: Abre o VS Code direto na pasta
            os.system(f"code {caminho_projeto} > /dev/null 2>&1 &")
            
        return f"✅ {mensagem}"

    except Exception as e:
        return f"❌ Erro ao criar projeto: {str(e)}"

def pegar_hora():
    return datetime.now().strftime("%H:%M")

# --- O MAESTRO (PROCESSA O PEDIDO) ---
def processar_comando(usuario_input):
    sistema = """
    Você é a Ursa, uma IA Desenvolvedora Sênior e Assistente Pessoal.
    Você tem acesso direto ao terminal do Linux (Pop!_OS).
    
    FERRAMENTAS DISPONÍVEIS (Responda APENAS JSON):
    1. { "funcao": "abrir_programa", "parametro": "nome" } -> Para abrir apps (brave, vscode, calc).
    2. { "funcao": "criar_projeto", "parametro": "nome_do_projeto|tipo" } -> Para criar novos projetos. 
       O parâmetro deve ser "Nome|Tipo". Ex: "LojaSorvete|python" ou "LandingPage|web".
    3. { "funcao": "pegar_hora", "parametro": "" }
    4. { "funcao": "responder", "parametro": "texto" } -> Para conversa normal.
    
    Se o usuário pedir para CRIAR um projeto, extraia o nome e a linguagem e use a função criar_projeto.
    Seja sarcástica e técnica nas respostas de texto.
    """

    print("🐻 Ursa pensando...", end="\r")
    
    try:
        response = client.chat.completions.create(
            model="llama3",
            messages=[
                {"role": "system", "content": sistema},
                {"role": "user", "content": usuario_input}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        resposta_raw = response.choices[0].message.content
        acao = json.loads(resposta_raw)
        
        funcao = acao.get("funcao")
        param = acao.get("parametro")
        
        print(f"🔧 Ação detectada: {funcao} ({param})") # Debug
        
        if funcao == "abrir_programa":
            return abrir_programa(param)
        
        elif funcao == "criar_projeto":
            if "|" in param:
                nome, tipo = param.split("|")
                return criar_projeto(nome.strip(), tipo.strip())
            else:
                return "❌ Erro: A IA não formatou o parâmetro corretamente para criar projeto."
                
        elif funcao == "pegar_hora":
            return f"⏰ {pegar_hora()}"
            
        elif funcao == "responder":
            return f"🐻: {param}"
            
    except Exception as e:
        return f"🐛 Bugou: {e}"

# --- LOOP PRINCIPAL ---
if __name__ == "__main__":
    # Garante que a pasta Projetos existe
    caminho_projetos = os.path.expanduser("~/Projetos")
    if not os.path.exists(caminho_projetos):
        os.makedirs(caminho_projetos)

    print("\n🐻 URSA V2 - BUILDER MODE ATIVADO")
    print(f"📂 Diretório de Projetos: {caminho_projetos}")
    print("Tente: 'Crie um projeto python chamado AutomaçãoZap' ou 'Abra o Brave'")
    
    while True:
        try:
            txt = input("\n👨‍💻 Você: ")
            if txt.lower() in ['sair', 'tchau']: break
            print(processar_comando(txt))
        except KeyboardInterrupt:
            break