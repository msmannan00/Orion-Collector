import json
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

with open("classifier.json", "r", encoding="utf-8") as f:
    classifier = json.load(f)

normalized_classifier = {}
for category, keywords in classifier.items():
    stems = set()
    for word in keywords:
        stems.add(stemmer.stem(word))
    normalized_classifier[category] = sorted(stems)

with open("classifier.json", "w", encoding="utf-8") as f:
    json.dump(normalized_classifier, f, indent=2, ensure_ascii=False)
