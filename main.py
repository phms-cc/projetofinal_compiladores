import spacy
import requests
from bs4 import BeautifulSoup
import random

def print_tree(sentence):
    """Função para imprimir a árvore sintática de uma sentença"""
    for token in sentence:
        if token.head == token:
            head_text = 'ROOT'
        else:
            head_text = token.head.text
        print(f"{token.text} ({tag_mappings.get(token.pos_, token.pos_)}) <-- {head_text} ({tag_mappings.get(token.head.pos_, token.head.pos_)})")

def get_sinonimos(word):
    try:
        url = f"http://www.sinonimos.com.br/{word}/"
        print(f"Obtendo sinonimos da URL: {url}")
        resposta = requests.get(url)
        soup = BeautifulSoup(resposta.text, 'html.parser')
        synonym_elements = soup.select('p.syn-list em.syn-number + a.sinonimo, p.syn-list span')
        sinonimos = [elem.text for elem in synonym_elements]
        return sinonimos
    except Exception as e:
        print(f"Error fetching sinonimos for {word}: {e}")
        return [word]  # Returns the original word in case of an error

# Função para reescrever uma sentença usando sinônimos
def reescrever_sentenca(sentence):
    doc = nlp(sentence)
    sentenca_reescrita = []
    for token in doc:
        if token.pos_ in ["VERB", "ADJ", "ADV"]:  # Considera substituir sinônimos para verbos, adjetivos e advérbios
            sinonimos = get_sinonimos(token.text)
            if sinonimos:
                if token.text.lower() == "mais":
                    sentenca_reescrita.append(token.text)
                    pass
                else :
                    # Adiciona um sinônimo aleatório
                    sentenca_reescrita.append(random.choice(sinonimos))
                    print(f"Sinônimos para {token.text}: {sinonimos}")
                    #sentenca_reescrita.append(sinonimos[0])  # Usa o primeiro sinônimo disponível  

            else:
                sentenca_reescrita.append(token.text)
        else:
            sentenca_reescrita.append(token.text)
    return " ".join(sentenca_reescrita)

# Carregar o modelo para português
nlp = spacy.load("pt_core_news_sm")

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

# Lê o conteúdo do arquivo de entrada
with open("t1.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Processa o texto com o modelo do Spacy
doc = nlp(text)

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

texto_reescrito = reescrever_sentenca(text)
print(f"\nTexto reescrito: {texto_reescrito}")