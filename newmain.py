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
import nltk
from nltk import CFG
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def classificar_sentenca(sentenca):
    doc = nlp(sentenca)
    classifications = [token.pos_ for token in doc if token.pos_ != 'SPACE']  
    return classifications

# TO DO : Implementar reoganização das frases em conjunto com a aplicação de sinonimos

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

def create_grammar():
    """Cria uma gramática adaptada para a língua portuguesa usando as tags do spaCy, incluindo pronomes, símbolos e outros terminais."""
    grammar = CFG.fromstring(
      """Texto -> Sentenca PONTUACAO_FINAL | Sentenca PONTUACAO_FINAL Texto
        Sentenca -> SintagmaNominal SintagmaVerbal | SintagmaVerbal SintagmaNominal | SintagmaNominal | SintagmaVerbal | SintagmaNominal SintagmaVerbal Conjuncao Sentenca | SintagmaVerbal Conjuncao Sentenca | SintagmaNominal SintagmaVerbal PronomeRelativo Sentenca
        SintagmaNominal -> Determinante Substantivo | Determinante Substantivo Adjetivo | Pronome | Substantivo | Substantivo Adjetivo | Determinante Substantivo Conjuncao Determinante Substantivo | Determinante Substantivo Conjuncao Determinante Substantivo | Determinante Numeral | Numeral | Determinante | Preposicao Substantivo | Substantivo | Substantivo | Numeral Substantivo | Numeral Substantivo Adjetivo | Preposicao Substantivo | Determinante Numeral | Numeral
        SintagmaVerbal -> Verbo | Verbo Adjetivo | Verbo Adverbio | Verbo SintagmaNominal | Verbo SintagmaNominal SintagmaNominal | Verbo Adverbio SintagmaNominal | Adverbio Verbo SintagmaNominal | Verbo Simbolo | Verbo SintagmaNominal Preposicao Determinante Substantivo Adjetivo | Verbo Substantivo Numeral | Verbo SintagmaNominal Preposicao Determinante Substantivo | Verbo SintagmaNominal Preposicao Determinante Substantivo Adjetivo | Adverbio Verbo SintagmaNominal Preposicao Substantivo
        Determinante -> 'DET'
        PronomeRelativo -> 'PRON'
        Substantivo -> 'NOUN' | 'PROPN'
        Pronome -> 'PRON'
        Adjetivo -> 'ADJ'
        Verbo -> 'VERB' | 'AUX' | 'AUX' 'VERB' 
        Adverbio -> 'ADV'
        Preposicao -> 'ADP'
        Conjuncao -> 'CCONJ' | 'SCONJ'
        Numeral -> 'NUM'
        Simbolo -> 'SYM'
        PONTUACAO_FINAL -> 'PUNCT'""")
    return grammar

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

def get_classificacao_gramatical_token(doc, token_text):
    """Função para obter a classificação gramatical de um token específico"""
    for token in doc:
        if token.text == token_text:
            tag_pt = tag_mappings.get(token.pos_, token.pos_)  # Obtém a tradução ou usa a original
            return tag_pt
    return None

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
 
    try:
        tools_button = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.ID, "hdtb-tls")) 
        )
        tools_button.click()
          
        result_stats = WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located((By.ID, "result-stats"))
        )
        print("Quantidade de resultados:", result_stats.text)
    except Exception as e:
        print("Erro ao tentar encontrar o botão de ferramentas ou a quantidade de resultados:", e)

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
with open("t1.txt", "r", encoding="utf-8") as file:
    text = file.read()

print("Texto original:")
print(text)

# Processa o texto com o modelo do Spacy
doc = nlp(text)

# Exibe a classificação gramatical de cada token
listar_tokens_classificacao(doc)

# Exibe Classificação gramatical da frase
classifications = classificar_sentenca(text)
print(f"Classificações gramaticais: {' '.join(classifications)}")

texto_reescrito = reescrever_sentenca(text)
print(f"\nTexto reescrito: {texto_reescrito}")

resultados = buscar_google_com_selenium(texto_reescrito)
# apenas exibir os 5 primeiros resultados
for url in resultados[:5]:
    print(url)