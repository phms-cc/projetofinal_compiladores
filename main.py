import spacy

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

def print_tree(sentence):
    """Função para imprimir a árvore sintática de uma sentença"""
    for token in sentence:
        if token.head == token:
            head_text = 'ROOT'
        else:
            head_text = token.head.text
        print(f"{token.text} ({tag_mappings.get(token.pos_, token.pos_)}) <-- {head_text} ({tag_mappings.get(token.head.pos_, token.head.pos_)})")

# Lê o conteúdo do arquivo de entrada
with open("acidente.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Processa o texto com o modelo do Spacy
doc = nlp(text)

# Lista os tokens e sua classificação gramatical
print("Tokens e classificação gramatical:")
for token in doc:
    tag_pt = tag_mappings.get(token.pos_, token.pos_)  # Obtém a tradução ou usa a original
    print(f" - {token.text}: {tag_pt}")

# Lista as entidades nomeadas no texto
print("\nEntidades nomeadas:")
for ent in doc.ents:
    entity_pt = entity_mappings.get(ent.label_, ent.label_)  # Obtém a tradução ou usa a original
    print(f" - {ent.text}: {entity_pt}")

# Analisa e imprime a árvore sintática de cada sentença
print("\nÁrvore sintática de cada sentença:")
for sent in doc.sents:
    print(f"\nSentença: {sent.text}")
    print_tree(sent)
