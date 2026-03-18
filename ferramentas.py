import os
import shutil
import subprocess
import warnings
from datetime import datetime
from openai import OpenAI

# ============================================================
# JARVIS IA — Módulo Ferramentas
# ============================================================
# Contém todas as funções que o Jarvis pode executar:
# pesquisa web, abertura de apps, criação de projetos, etc.
# ============================================================

# Suprime ResourceWarning de subprocessos desvinculados (esperado)
warnings.filterwarnings("ignore", category=ResourceWarning)

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        print("⚠️ AVISO: Nenhuma lib de busca encontrada.")
        print("⚠️ Execute: pip install -U ddgs")
        DDGS = None

client = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

# ============================================================
# SUB-AGENTE: GERADOR DE CÓDIGO
# ============================================================
def gerar_codigo_inteligente(linguagem: str, instrucoes: str) -> str:
    """
    Chama o LLM para gerar código limpo baseado na descrição.
    Segue boas práticas: nomes descritivos, comentários,
    tratamento de erros e estrutura organizada.
    """
    print(f"\n🧠 Jarvis Coding: Gerando código {linguagem} para '{instrucoes}'...")

    prompt_code = f"""
    Você é um engenheiro de software sênior.
    Gere APENAS o código {linguagem} para: "{instrucoes}".

    REGRAS OBRIGATÓRIAS:
    1. Sem markdown (```). Sem explicações. Código puro.
    2. Use nomes de variáveis e funções descritivos.
    3. Inclua comentários breves explicando blocos importantes.
    4. Adicione tratamento de erros onde necessário.
    5. Siga as convenções da linguagem (PEP8 para Python, etc).
    6. Se for Python, inclua if __name__ == '__main__'.
    """
    
    try:
        response = client.chat.completions.create(
            model="llama3",
            messages=[{"role": "user", "content": prompt_code}],
            temperature=0.2 
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"# Erro ao gerar código: {e}"

# ============================================================
# FERRAMENTAS DO SISTEMA
# ============================================================

def abrir_programa(nome_programa: str) -> str:
    """Abre um aplicativo pelo nome, com fallback para Flatpak."""
    nome = nome_programa.lower().strip()
    print(f"🔍 Jarvis: Localizando '{nome}' no sistema...")

    # Mapa de aplicativos com suporte híbrido (Nativo + Flatpak)
    mapa = {
        "navegador": ["brave-browser", "flatpak run com.brave.Browser", "google-chrome", "firefox"],
        "brave": ["brave-browser", "flatpak run com.brave.Browser"],
        
        "vscode": ["code", "flatpak run com.visualstudio.code"],
        "code": ["code"],
        "visual studio code": ["code"],
        
        "calculadora": ["gnome-calculator", "flatpak run org.gnome.Calculator"],
        "calc": ["gnome-calculator", "flatpak run org.gnome.Calculator"], 
        "calculator": ["gnome-calculator", "flatpak run org.gnome.Calculator"],
        
        "terminal": ["gnome-terminal", "x-terminal-emulator", "konsole"],
        "console": ["gnome-terminal", "x-terminal-emulator", "konsole"], # Sinônimo importante
        
        "arquivos": ["xdg-open .", "nautilus", "dolphin"],
        "nautilus": ["xdg-open .", "nautilus"],
        "explorer": ["xdg-open ."]
    }
    
    comandos_tentar = mapa.get(nome, [nome])
    
    for cmd in comandos_tentar:
        # Verifica se o comando existe no sistema (shutil.which) OU se é um comando composto com espaços (ex: flatpak run)
        if " " in cmd or shutil.which(cmd):
            try:
                # CORREÇÃO SÊNIOR: start_new_session=True desvincula o processo filho.
                # Isso impede que o terminal fique preso e remove os ResourceWarnings.
                subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                return f"✅ Sucesso: Abri '{nome}'."
            except Exception:
                pass
            
    return f"❌ Erro: Não encontrei '{nome}' instalado."

def pesquisar_web(termo: str) -> str:
    """
    Pesquisa rápida via terminal (DuckDuckGo).
    Retorna dados brutos para o LLM processar (fluxo RAG).
    Ideal para consultas leves sem necessidade de imagens.
    """
    if not DDGS:
        return "❌ Erro: Biblioteca de busca não instalada."

    print(f"🌐 Jarvis Web (Terminal): Pesquisando '{termo}'...")

    try:
        results = DDGS().text(termo, region='br-pt', max_results=5)

        if not results:
            return f"Sem resultados para '{termo}'."

        # Formata os resultados de forma legível para o LLM
        dados = []
        for i, r in enumerate(results, 1):
            titulo = r.get('title', 'Sem título')
            corpo = r.get('body', 'Sem conteúdo')
            link = r.get('href', '')
            dados.append(f"Resultado {i}:\nTítulo: {titulo}\nConteúdo: {corpo}\nFonte: {link}")

        return "\n\n".join(dados)

    except Exception as e:
        return f"Erro na pesquisa web: {str(e)}"

def pesquisar_navegador(termo: str) -> str:
    """
    Pesquisa completa via navegador Brave.
    Abre o Brave com a busca para conteúdo visual, extenso
    ou que necessite navegação interativa.
    """
    print(f"🌐 Jarvis Browser: Abrindo pesquisa para '{termo}'...")

    url = f"https://search.brave.com/search?q={termo.replace(' ', '+')}"
    
    comandos_possiveis = [
        ["brave-browser", url],
        ["flatpak", "run", "com.brave.Browser", url],
        ["google-chrome", url],
        ["xdg-open", url]
    ]

    for cmd_lista in comandos_possiveis:
        binario = cmd_lista[0]
        
        # Verifica binário ou assume que flatpak existe
        if binario == "flatpak" or shutil.which(binario):
            try:
                # Usa subprocess com sessão nova para garantir abertura limpa
                subprocess.Popen(cmd_lista, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                return f"✅ Pesquisa aberta no navegador: {termo}"
            except Exception as e:
                print(f"DEBUG: Falha no cmd {binario}: {e}")

    return "❌ Erro: Não consegui abrir nenhum navegador para pesquisa."

def criar_projeto(dados_projeto: dict) -> str:
    """
    Cria um projeto de software completo a partir de uma descrição.
    Gera a estrutura de pastas, código inicial via LLM e abre no VS Code.
    """
    if not isinstance(dados_projeto, dict):
        return "❌ Erro: Parâmetros inválidos."

    nome = dados_projeto.get("nome", "ProjetoSemNome")
    tipo = dados_projeto.get("tipo", "texto")
    desc = dados_projeto.get("desc", "Projeto criado pelo Jarvis")
    
    base_path = os.path.expanduser("~/Projetos")
    caminho_projeto = os.path.join(base_path, nome)
    
    try:
        if not os.path.exists(caminho_projeto):
            os.makedirs(caminho_projeto)
        
        arquivo_init = ""
        conteudo = ""
        
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
            
        # Tenta abrir o VS Code usando subprocess também
        if shutil.which("code"):
            subprocess.Popen(["code", caminho_projeto], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            
        return f"✅ Projeto '{nome}' criado!\n📂 Arquivo: {arquivo_init}\n🧠 IA programou: \"{desc}\""

    except Exception as e:
        return f"❌ Erro ao criar projeto: {str(e)}"

def pegar_hora():
    return datetime.now().strftime("%H:%M")