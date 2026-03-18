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
    """Tenta abrir programas de forma inteligente com dicionário de sinônimos"""
    # 1. Normaliza para minúsculo e tira espaços extras
    nome = nome_programa.lower().strip()
    
    print(f"DEBUG: A IA pediu para abrir: '{nome}'") # Para a gente ver o que ela mandou
    
    # 2. Mapa de Sinônimos -> Lista de Comandos para tentar
    # A chave é o que a IA pode mandar. O valor é a lista de comandos do Linux.
    mapa = {
        # Navegadores
        "navegador": ["brave-browser", "brave-browser-stable", "flatpak run com.brave.Browser", "google-chrome", "firefox"],
        "brave": ["brave-browser", "brave-browser-stable", "flatpak run com.brave.Browser"],
        "chrome": ["google-chrome", "google-chrome-stable"],
        "firefox": ["firefox"],
        
        # Editores
        "vscode": ["code", "flatpak run com.visualstudio.code"],
        "code": ["code"],
        
        # Calculadora (Aqui estava o erro! Adicionei variações)
        "calculadora": ["gnome-calculator", "flatpak run org.gnome.Calculator"],
        "calc": ["gnome-calculator", "flatpak run org.gnome.Calculator"], 
        "calculator": ["gnome-calculator", "flatpak run org.gnome.Calculator"],
        
        # Terminal (Várias tentativas para garantir)
        "terminal": ["gnome-terminal", "konsole", "xterm", "tilix"],
        "console": ["gnome-terminal"],
        
        # Gerenciador de Arquivos
        "arquivos": ["nautilus", "dolphin", "thunar"],
        "nautilus": ["nautilus"],
        "explorer": ["nautilus"], # Caso ela ache que é Windows
        "gerenciador de arquivos": ["nautilus"]
    }
    
    # Busca a lista de comandos usando a chave OU usa o próprio nome como comando
    comandos_tentar = mapa.get(nome, [nome])
    
    for cmd in comandos_tentar:
        # Verifica se é comando composto (tem espaço) OU se o comando existe no sistema (shutil.which)
        if " " in cmd or shutil.which(cmd):
            print(f"DEBUG: Tentando executar comando real: {cmd}")
            # O nohup ajuda a desvincular o processo da Ursa (evita travar)
            os.system(f"nohup {cmd} > /dev/null 2>&1 &") 
            return f"✅ Sucesso: Abri '{nome}'."
            
    return f"❌ Erro: Tentei abrir '{nome}' (comandos: {comandos_tentar}) mas não encontrei instalado."

def criar_projeto(nome_projeto, tipo):
    """Cria uma pasta e um arquivo inicial básico"""
    base_path = os.path.expanduser("~/Projetos")
    caminho_projeto = os.path.join(base_path, nome_projeto)
    
    try:
        # Cria a pasta se não existir
        if not os.path.exists(caminho_projeto):
            os.makedirs(caminho_projeto)
        
        mensagem = f"Pasta criada em {caminho_projeto}. "
        
        # Define o conteúdo baseado no tipo
        arquivo_init = ""
        conteudo = ""
        
        if "python" in tipo.lower():
            arquivo_init = "main.py"
            conteudo = "print('Hello World - Criado pela Ursa 🐻')\n# Comece a codar aqui, Otávio!"
        elif "web" in tipo.lower() or "html" in tipo.lower() or "site" in tipo.lower():
            arquivo_init = "index.html"
            conteudo = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Projeto Ursa</title>
</head>
<body>
    <h1>Olá, Otávio! 🐻</h1>
    <p>Projeto Web iniciado com sucesso.</p>
</body>
</html>"""
        elif "texto" in tipo.lower():
            arquivo_init = "notas.txt"
            conteudo = "Ideias do projeto..."
            
        # Cria o arquivo
        if arquivo_init:
            caminho_arq = os.path.join(caminho_projeto, arquivo_init)
            with open(caminho_arq, "w") as f:
                f.write(conteudo)
            mensagem += f"Arquivo {arquivo_init} criado."
            
            # Tenta abrir o VS Code na pasta
            if shutil.which("code"):
                os.system(f"code {caminho_projeto} > /dev/null 2>&1 &")
                mensagem += " VS Code aberto."
            
        return f"✅ {mensagem}"

    except Exception as e:
        return f"❌ Erro ao criar projeto: {str(e)}"

def pegar_hora():
    return datetime.now().strftime("%H:%M")

# --- O MAESTRO ---
def processar_comando(usuario_input):
    sistema = """
    Você é a Ursa, uma IA Desenvolvedora Sênior no Pop!_OS.
    
    FERRAMENTAS (Responda APENAS JSON):
    1. { "funcao": "abrir_programa", "parametro": "nome_app" } 
       Use para: navegador, vscode, calculadora, terminal, arquivos.
       IMPORTANTE: Envie nomes simples. Ex: "calculadora", "terminal".
       
    2. { "funcao": "criar_projeto", "parametro": "NomeProjeto|tipo" }
       Tipos: python, web, texto.
       
    3. { "funcao": "pegar_hora", "parametro": "" }
    4. { "funcao": "responder", "parametro": "texto" }
    
    Seja breve e técnica.
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
        
        # Debug para a gente ver no terminal o que está rolando
        print(f"🔧 Ação: {funcao} | Param: {param}" + " " * 20) 
        
        if funcao == "abrir_programa":
            return abrir_programa(param)
        
        elif funcao == "criar_projeto":
            if "|" in param:
                nome, tipo = param.split("|")
                return criar_projeto(nome.strip(), tipo.strip())
            else:
                return "❌ Erro: Formato inválido. Use Nome|Tipo."
                
        elif funcao == "pegar_hora":
            return f"⏰ {pegar_hora()}"
            
        elif funcao == "responder":
            return f"🐻: {param}"
            
    except Exception as e:
        return f"🐛 Erro Crítico: {e}"

# --- LOOP ---
if __name__ == "__main__":
    caminho_projetos = os.path.expanduser("~/Projetos")
    if not os.path.exists(caminho_projetos):
        os.makedirs(caminho_projetos)

    print("\n🐻 URSA V4 - FINALMENTE ESTÁVEL")
    print(f"📂 Pasta de Projetos: {caminho_projetos}")
    print("------------------------------------------------")
    
    while True:
        try:
            txt = input("\n👨‍💻 Você: ")
            if txt.lower() in ['sair', 'tchau']: break
            print(processar_comando(txt))
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break