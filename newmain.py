import spacy
import requests
from bs4 import BeautifulSoup
import random
from googlesearch import search

def get_sinonimos(word):
    try:
        url = f"http://www.sinonimos.com.br/{word}/"
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
            print("sinonimos: ", sinonimos)
            if sinonimos and token.text.lower() != "mais":
                sin = random.choice(sinonimos)
                print(f"Usando '{sin}' no lugar de '{token.text}'")
                sentenca_reescrita.append(sin)
            else:
                sentenca_reescrita.append(token.text)
        else:
            sentenca_reescrita.append(token.text)
    return " ".join(sentenca_reescrita)

def buscar_no_google(query):
    print(f"\nBuscando no Google por: {query}")
    resultados = search(query, num_results=3)
    return resultados

# Carregar o modelo para português
nlp = spacy.load("pt_core_news_sm")

# Lê o conteúdo do arquivo de entrada
with open("t2.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Processa o texto com o modelo do Spacy
doc = nlp(text)

texto_reescrito = reescrever_sentenca(text)
print(f"\nTexto reescrito: {texto_reescrito}")

# Realizar a pesquisa no Google e exibir os resultados
urls = buscar_no_google(texto_reescrito)
print("\nURLs dos 5 primeiros resultados:")
for url in urls:
    print(url)