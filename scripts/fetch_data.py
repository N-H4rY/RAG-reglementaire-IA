"""Vérifie le corpus dans data/raw/ et télécharge les PDF EUR-Lex/CNIL directs.

Les pages web (fiches CNIL, avis EDPB) sont à enregistrer en PDF depuis
l'URL indiquée dans data/SOURCES.md, puis à placer dans data/raw/.
"""
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

# Téléchargement direct possible
DIRECT = {
    "rgpd.pdf": "https://eur-lex.europa.eu/legal-content/FR/TXT/PDF/?uri=CELEX:32016R0679",
    "ai_act.pdf": "https://eur-lex.europa.eu/legal-content/FR/TXT/PDF/?uri=CELEX:32024R1689",
    "data_act.pdf": "https://eur-lex.europa.eu/legal-content/FR/TXT/PDF/?uri=CELEX:32023R2854",
    "cnil_checklist_ia.pdf": "https://www.cnil.fr/sites/default/files/2025-07/ia_liste_de_verification.pdf",
}


def expected_files() -> list[str]:
    """Noms de fichiers listés dans data/SOURCES.md."""
    text = (ROOT / "data" / "SOURCES.md").read_text(encoding="utf-8")
    return re.findall(r"^\| ([\w\-]+\.pdf) \|", text, flags=re.M)


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    for name, url in DIRECT.items():
        target = RAW / name
        if target.exists():
            continue
        print(f"téléchargement de {name}")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            target.write_bytes(r.read())
    missing = [n for n in expected_files() if not (RAW / n).exists()]
    for n in missing:
        print(f"manquant : {n} (voir data/SOURCES.md)")
    print("corpus complet" if not missing else f"{len(missing)} fichier(s) manquant(s)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
