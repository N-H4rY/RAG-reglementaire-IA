# RAG réglementaire IA

Assistant de questions-réponses (RAG) sur des documents réglementaires liés à l'IA et aux données personnelles : RGPD, AI Act, Data Act, avis EDPB et fiches pratiques de la CNIL. Le projet mesure la qualité de la récupération et des réponses avec des métriques quantitatives (Recall@k, MRR, fidélité) plutôt qu'à l'œil, et compare plusieurs configurations (taille de chunks, top-k, dense seul vs hybride, avec ou sans reranker).

## Corpus

13 documents en français : RGPD, AI Act, Data Act, avis EDPB 28/2024, recommandations CNIL et plusieurs fiches pratiques IA de la CNIL (qualification des acteurs, base légale, analyse d'impact, intérêt légitime, moissonnage, sécurité, statut d'un modèle). Le corpus est volontairement croisé pour permettre des questions qui recoupent plusieurs textes.

Les PDF ne sont pas versionnés. Les sources (nom, URL d'origine) sont listées dans [data/SOURCES.md](data/SOURCES.md). `python scripts/fetch_data.py` télécharge ce qui peut l'être directement et signale ce qui reste à récupérer manuellement.

## Architecture

```
src/
  config.py       # chargement de config.yaml
  ingestion.py     # extraction PyMuPDF, nettoyage, métadonnées (document, page, article)
  chunking.py      # découpage en chunks, taille et chevauchement paramétrables
  indexing.py      # embeddings + index FAISS, index BM25
  retrieval.py     # recherche dense, hybride, reranking
  generation.py    # prompt + LLM, réponse avec citations
  evaluation.py    # Recall@k, MRR, fidélité et exactitude des réponses
eval/              # jeu de questions-réponses de référence, résultats des expériences
notebooks/         # analyse des résultats et des erreurs
app/               # démo Streamlit
```

Tous les paramètres (chunking, top-k, modèles, seed) sont centralisés dans `config.yaml` pour que les expériences soient reproductibles.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copier `.env.example` en `.env` et renseigner les clés si besoin (voir section LLM).

## Utilisation

```bash
python scripts/fetch_data.py   # vérifie / complète le corpus dans data/raw/
python -m src.ingestion         # extrait le texte, affiche des statistiques par document
```

Les étapes de chunking, d'indexation, de génération et d'évaluation seront documentées ici au fur et à mesure.

## LLM

Le générateur tourne par défaut en local via [Ollama](https://ollama.com) (modèle léger de type `qwen2.5:3b`, adapté à une machine sans GPU). L'API Claude peut être utilisée en alternative, notamment comme juge pour l'évaluation de la fidélité des réponses ; dans ce cas la clé se place dans `.env`, jamais dans le dépôt.

## État du projet

Projet académique en cours de construction, avancé étape par étape : ingestion terminée, chunking et indexation à venir.
