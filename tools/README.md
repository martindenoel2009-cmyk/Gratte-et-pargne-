# Outils de fabrication des vidéos

- `make.py` : moteur (dessins Maxime, carte à gratter, tirelire, texte mot par mot, bruitages). Exemple complet : vidéo « Défi 30 jours ».
- `make20.py` : exemple de vidéo qui réutilise le moteur avec d'autres scènes (`import make as m`, on remplace `m.SCENES` et `m.illus`).

Usage : `python3 make.py dossier contact` (planche de contrôle) puis `python3 make.py dossier all` → `dossier/final.mp4` (1080x1920, 30 fps, bruitages, sans musique ni voix).
Les vidéos publiées vont dans `videos/AAAA-MM-JJ_HH.mp4`.
