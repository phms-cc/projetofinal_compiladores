import spacy
import requests
from bs4 import BeautifulSoup
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib.parse
from bs4 import BeautifulSoup
import os

# Mapeamentos para tradução das etiquetas de classificação gramatical
tag_mappings = {
    "PROPN": "Nome Próprio",
    "AUX": "Auxiliar",
    "DET": "Determinante",
    "NOUN": "Substantivo",
    "ADJ": "Adjetivo",
    "PUNCT": "Pontuação",
    "ADP": "Preposição",
    "NUM": "Numeral",
    "ADV": "Advérbio",
    "CCONJ": "Conjunção Coordenativa",
    "VERB": "Verbo",
    "PRON": "Pronome",
    "SCONJ": "Conjunção Subordinativa",
}

# Mapeamentos para tradução dos tipos de entidades nomeadas
entity_mappings = {
    "LOC": "Local",
    "ORG": "Organização",
    "PER": "Pessoa",
    "DATE": "Data",
    "TIME": "Hora",
    "MISC": "Diversos"
}

def print_tree(sentence):
    """Função para imprimir a árvore sintática de uma sentença"""
    for token in sentence:
        if token.head == token:
            head_text = 'ROOT'
        else:
            head_text = token.head.text
        print(f"{token.text} ({tag_mappings.get(token.pos_, token.pos_)}) <-- {head_text} ({tag_mappings.get(token.head.pos_, token.head.pos_)})")

def listar_tokens_classificacao(doc):
    """Função para listar os tokens e sua classificação gramatical""" 
    print("Tokens e classificação gramatical:")
    for token in doc:
        tag_pt = tag_mappings.get(token.pos_, token.pos_)  # Obtém a tradução ou usa a original
        print(f" - {token.text}: {tag_pt}")

def listar_entidades_nomeadas(doc):
    """Função para listar as entidades nomeadas no texto"""
    print("Entidades nomeadas:")
    for ent in doc.ents:
        entity_pt = entity_mappings.get(ent.label_, ent.label_)  # Obtém a tradução ou usa a original
        print(f" - {ent.text}: {entity_pt}")    

def arvore_sintatica(doc):
    """Função para imprimir a árvore sintática de cada sentença"""
    print("\nÁrvore sintática de cada sentença:")
    for sent in doc.sents:
        print(f"\nSentença: {sent.text}")
        print_tree(sent)

# termos que não devem ser substituídos por sinônimos
termos_excluidos = ["mais", "menos"]

# Função para buscar no Google com Selenium
def buscar_google_com_selenium(query):
    # Configurações do navegador
    chrome_options = Options()
    chrome_options.headless = True  # Modo headless para não abrir janela do navegador
    chrome_options.add_argument('log-level=3')

    # Redirecionar os logs de WebDriver para /dev/null (Unix) ou NUL (Windows)
    log_path = "NUL" if os.name == 'nt' else "/dev/null"
    service = Service(ChromeDriverManager().install(), log_path=log_path)
    service.suppress_welcome_message = True  # Suprimir mensagem de boas-vindas do ChromeDriver

    # Iniciar WebDriver com as configurações de log
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Acessar o Google
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    driver.get(url)

    # Aguardar para a página carregar completamente
    time.sleep(1)  

    # Obter o HTML da página
    html_content = driver.page_source
    driver.quit()

    # Usar BeautifulSoup para analisar o HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    links = []
    for item in soup.find_all('a', jsname='UWckNb'):
        href = item.get('href')
        if href and "http" in href:
            links.append(href)
    return links

# Função para buscar sinônimos de uma palavra em um site
def get_sinonimos(word):
    try:
        url = f"http://www.sinonimos.com.br/{word.lower()}/"
        print(f"Obtendo sinonimos da URL: {url}")
        resposta = requests.get(url)
        soup = BeautifulSoup(resposta.text, 'html.parser')
        synonym_elements = soup.select('p.syn-list a.sinonimo')
        sinonimos = [elem.text.strip() for elem in synonym_elements]
        return sinonimos
    except Exception as e:
        print(f"Erro ao buscar sinônimos para {word}: {e}")
        return [word]  # Returns the original word in case of an error

# Função para reescrever uma sentença usando sinônimos
def reescrever_sentenca(sentence):
    doc = nlp(sentence)
    sentenca_reescrita = []
    for token in doc:
        if token.pos_ in ["VERB", "ADJ", "ADV"]:
            sinonimos = get_sinonimos(token.text)
            if sinonimos and token.text.lower() != "mais" and token.text.lower() != "menos":
                sin = random.choice(sinonimos)
                print(f"Usando '{sin}' no lugar de '{token.text}'")
                sentenca_reescrita.append(sin)
            else:
                sentenca_reescrita.append(token.text)
        else:
            sentenca_reescrita.append(token.text)
    return " ".join(sentenca_reescrita)

# Carregar o modelo para português
nlp = spacy.load("pt_core_news_sm")

# Lê o conteúdo do arquivo de entrada
with open("acidente.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Processa o texto com o modelo do Spacy
doc = nlp(text)

texto_reescrito = reescrever_sentenca(text)
print(f"\nTexto reescrito: {texto_reescrito}")

resultados = buscar_google_com_selenium(texto_reescrito)
# apenas exibir os 5 primeiros resultados
for url in resultados[:5]:
    print(url)