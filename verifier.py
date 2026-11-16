"""Vérifications automatiques de diagnostic.py.

Chaque assert vérifie un résultat attendu. Si l'un d'eux est faux, Python
s'arrête avec une AssertionError et un code de sortie différent de 0 :
la CI passe au rouge.
"""
import tempfile
from pathlib import Path

from diagnostic import analyser, categorie, taille_lisible

# 1. La catégorie d'un fichier
assert categorie("script.py") == "python"
assert categorie("NOTES.TXT") == "texte"
assert categorie("erreurs.log") == "log"
assert categorie("photo.jpg") == "autre"
assert categorie("Makefile") == "autre"
print("OK categorie")

# 2. Les tailles lisibles
assert taille_lisible(0) == "0 o"
assert taille_lisible(512) == "512 o"
assert taille_lisible(1536) == "1.5 Ko"
assert taille_lisible(10240) == "10.0 Ko"
assert taille_lisible(3 * 1024 * 1024) == "3.0 Mo"
print("OK taille_lisible")

# 3. L'analyse d'un vrai dossier, fabriqué pour l'occasion
with tempfile.TemporaryDirectory() as dossier:
    racine = Path(dossier)
    (racine / "a.py").write_text("print('a')\n")
    (racine / "notes.txt").write_text("x" * 100)
    (racine / "sous-dossier").mkdir()
    (racine / "sous-dossier" / "app.log").write_text("")
    (racine / "sous-dossier" / "gros.bin").write_bytes(bytes(6 * 1024 * 1024))
    stats = analyser(dossier)
    assert stats["total"] == 4
    assert stats["python"] == 1
    assert stats["texte"] == 1
    assert stats["log"] == 1
    assert stats["autre"] == 1
    assert stats["gros"] == ["gros.bin"]
print("OK analyser")

print("Toutes les vérifications sont passées.")
