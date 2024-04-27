import spacy

# Carrega o modelo do Spacy para a língua portuguesa
nlp = spacy.load("pt_core_news_sm")

# Lê o conteúdo do arquivo de entrada
with open("teste.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Processa o texto com o modelo do Spacy
doc = nlp(text)

# Lista os tokens e sua classificação gramatical
print("Tokens e classificação gramatical:")
for token in doc:
    print(f" - {token.text}: {token.pos_}")

# Lista as entidades nomeadas no texto
print("\nEntidades nomeadas:")
for ent in doc.ents:
    print(f" - {ent.text}: {ent.label_}")