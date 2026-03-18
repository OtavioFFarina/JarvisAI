import os
import json
import shutil
from openai import OpenAI
from datetime import datetime

# --- Configuração do Cérebro ---
client = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

# --- SUB-AGENTE: GERADOR DE CÓDIGO ---
def gerar_codigo_inteligente(linguagem, instrucoes):
    """
    Esta função chama a IA novamente APENAS para escrever o código do arquivo.
    Isso é o que chamamos de 'Agentic Workflow'.
    """
    print(f"\n🧠 Ursa Coding: Escrevendo código {linguagem} para '{instrucoes}'...")
    
    prompt_code = f"""
    Você é um Expert em Programação.
    Gere APENAS o código {linguagem} para atender a seguinte instrução:
    "{instrucoes}"
    
    REGRAS:
    1. NÃO explique nada. NÃO coloque markdown (```).
    2. Apenas o código puro pronto para salvar em arquivo.
    3. Se for Python, inclua prints para mostrar o resultado.
    """
    
    try:
        response = client.chat.completions.create(
            model="llama3",
            messages=[{"role": "user", "content": prompt_code}],
            temperature=0.2 # Baixa criatividade para código preciso
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"# Erro ao gerar código: {e}"

# --- FERRAMENTAS DO SISTEMA ---

def abrir_programa(nome_programa):
    nome = nome_programa.lower().strip()
    print(f"DEBUG: A IA pediu para abrir: '{nome}'") 
    
    mapa = {
        "navegador": ["brave-browser", "flatpak run com.brave.Browser", "google-chrome"],
        "brave": ["brave-browser", "flatpak run com.brave.Browser"],
        
        # AQUI O FIX DO "CODE": Adicionei explicitamente variações
        "vscode": ["code", "flatpak run com.visualstudio.code"],
        "code": ["code"],
        "visual studio code": ["code"],
        
        "calculadora": ["gnome-calculator", "flatpak run org.gnome.Calculator"],
        "calc": ["gnome-calculator", "flatpak run org.gnome.Calculator"], 
        "calculator": ["gnome-calculator", "flatpak run org.gnome.Calculator"],
        
        "terminal": ["gnome-terminal", "x-terminal-emulator", "konsole"],
        "arquivos": ["xdg-open .", "nautilus", "dolphin"],
        "nautilus": ["xdg-open .", "nautilus"]
    }
    
    comandos_tentar = mapa.get(nome, [nome])
    
    for cmd in comandos_tentar:
        if " " in cmd or shutil.which(cmd):
            print(f"DEBUG: Tentando executar: {cmd}")
            try:
                os.system(f"nohup {cmd} > /dev/null 2>&1 &") 
                return f"✅ Sucesso: Abri '{nome}'."
            except Exception:
                pass
            
    return f"❌ Erro: Não encontrei '{nome}' instalado."

def criar_projeto(dados_projeto):
    """
    Agora recebe um dicionário: { 'nome': '...', 'tipo': '...', 'desc': '...' }
    """
    nome = dados_projeto.get("nome", "ProjetoSemNome")
    tipo = dados_projeto.get("tipo", "texto")
    desc = dados_projeto.get("desc", "Projeto criado pela Ursa")
    
    base_path = os.path.expanduser("~/Projetos")
    caminho_projeto = os.path.join(base_path, nome)
    
    try:
        if not os.path.exists(caminho_projeto):
            os.makedirs(caminho_projeto)
        
        arquivo_init = ""
        conteudo = ""
        
        # Chama a IA para gerar o conteúdo baseado na descrição do usuário
        conteudo_gerado = gerar_codigo_inteligente(tipo, desc)
        
        if "python" in tipo.lower():
            arquivo_init = "main.py"
            conteudo = conteudo_gerado
        elif "web" in tipo.lower() or "html" in tipo.lower():
            arquivo_init = "index.html"
            conteudo = conteudo_gerado
        else:
            arquivo_init = "info.txt"
            conteudo = desc
            
        caminho_arq = os.path.join(caminho_projeto, arquivo_init)
        with open(caminho_arq, "w") as f:
            f.write(conteudo)
            
        # Abre o VS Code
        if shutil.which("code"):
            os.system(f"code {caminho_projeto} > /dev/null 2>&1 &")
            
        return f"✅ Projeto '{nome}' criado!\n📂 Arquivo: {arquivo_init}\n🧠 IA programou: \"{desc}\""

    except Exception as e:
        return f"❌ Erro ao criar projeto: {str(e)}"

def pegar_hora():
    return datetime.now().strftime("%H:%M")

def processar_comando(usuario_input):
    sistema = """
    Você é a Ursa, IA Desenvolvedora Sênior (V4.0).
    Responda APENAS JSON.
    
    FERRAMENTAS:
    1. { "funcao": "abrir_programa", "parametro": "nome_simples" }
       (Ex: code, navegador, terminal, calc)
       
    2. { "funcao": "criar_projeto", "parametro": { "nome": "NomeSemEspaco", "tipo": "python|web", "desc": "Instruções do que o código deve fazer" } }
       ATENÇÃO: O parâmetro de criar_projeto AGORA É UM OBJETO JSON, não string.
       Exemplo: { "funcao": "criar_projeto", "parametro": { "nome": "SomaZap", "tipo": "python", "desc": "Some dois números e mostre na tela" } }
       
    3. { "funcao": "pegar_hora", "parametro": "" }
    4. { "funcao": "responder", "parametro": "texto" }
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
        
        print(f"🔧 Ação: {funcao} | Param: {str(param)[:50]}...") 
        
        if funcao == "abrir_programa":
            return abrir_programa(param)
        
        elif funcao == "criar_projeto":
            # Agora param já vem como dicionário/objeto graças ao prompt novo
            if isinstance(param, dict):
                return criar_projeto(param)
            else:
                return "❌ Erro: A IA não enviou os detalhes do projeto corretamente."
                
        elif funcao == "pegar_hora":
            return f"⏰ {pegar_hora()}"
            
        elif funcao == "responder":
            return f"🐻: {param}"
            
    except Exception as e:
        return f"🐛 Erro: {e}"

if __name__ == "__main__":
    caminho_projetos = os.path.expanduser("~/Projetos")
    if not os.path.exists(caminho_projetos):
        os.makedirs(caminho_projetos)

    print("\n🐻 URSA V4.0 - GENIUS MODE")
    print(f"📂 Pasta: {caminho_projetos}")
    print("------------------------------------------------")
    
    while True:
        try:
            txt = input("\n👨‍💻 Você: ")
            if txt.lower() in ['sair', 'tchau']: break
            print(processar_comando(txt))
        except KeyboardInterrupt:
            break