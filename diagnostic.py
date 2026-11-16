"""Diagnostic d'un dossier : compte les fichiers et publie un rapport HTML.

Usage : python3 diagnostic.py <dossier à analyser> <dossier de sortie>
"""
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

LIMITE = 5 * 1024 * 1024   # 5 Mo


def categorie(nom):
    """Renvoie la catégorie d'un fichier d'après son extension."""
    extension = Path(nom).suffix.lower()
    if extension == ".py":
        return "python"
    elif extension == ".txt":
        return "texte"
    elif extension == ".log":
        return "log"
    return "autre"


def taille_lisible(octets):
    """Renvoie une taille lisible : 512 o, 1.5 Ko, 3.2 Mo..."""
    if octets < 1024:
        return f"{octets} o"
    elif octets < 1024 ** 2:
        return f"{octets / 1024:.1f} Ko"
    return f"{octets / 1024 ** 2:.1f} Mo"


def analyser(dossier, ignorer=()):
    """Parcourt le dossier et ses sous-dossiers, et renvoie les statistiques."""
    stats = {"total": 0, "taille": 0, "python": 0, "texte": 0, "log": 0, "autre": 0, "gros": []}
    for f in sorted(Path(dossier).rglob("*")):
        # On saute l'historique Git et les dossiers à ignorer (le rapport lui-même)
        if not f.is_file() or ".git" in f.parts or any(i in f.parts for i in ignorer):
            continue
        taille = f.stat().st_size
        stats["total"] += 1
        stats["taille"] += taille
        stats[categorie(f.name)] += 1
        if taille > LIMITE:
            stats["gros"].append(f.name)
    return stats


def page_html(stats):
    """Fabrique la page HTML du rapport."""
    date = datetime.now(ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y à %H:%M")
    if stats["gros"]:
        etat = "Attention : fichiers volumineux détectés"
    else:
        etat = "Dossier propre"
    lignes = ""
    for cle in ["python", "texte", "log", "autre"]:
        lignes += f"<tr><td>{cle}</td><td>{stats[cle]}</td></tr>\n"
    return f"""<!doctype html>
<html lang="fr">
<head><meta charset="utf-8"><title>Diagnostic AstraCorp</title></head>
<body>
<h1>Diagnostic AstraCorp</h1>
<p>Rapport généré le {date}, heure de Paris.</p>
<p><strong>{etat}</strong></p>
<p>{stats["total"]} fichiers, {taille_lisible(stats["taille"])} au total.</p>
<table>
<tr><th>Catégorie</th><th>Fichiers</th></tr>
{lignes}</table>
</body>
</html>
"""


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage : python3 diagnostic.py <dossier> <sortie>")
        sys.exit(1)
    dossier = sys.argv[1]
    sortie = Path(sys.argv[2])
    stats = analyser(dossier, ignorer=[sortie.name])
    sortie.mkdir(parents=True, exist_ok=True)
    (sortie / "index.html").write_text(page_html(stats), encoding="utf-8")
    print(f"Rapport écrit dans {sortie / 'index.html'} : {stats['total']} fichiers")
