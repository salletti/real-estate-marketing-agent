# domain/

Ce dossier contient les **entités métier** et les **règles de gestion** du projet.

Il est indépendant de FastAPI, de la base de données et de tout framework externe.

**Exemples futurs :**
- `property.py` — entité `Property` (adresse, surface, prix, etc.)
- `listing.py` — entité `Listing` (annonce générée, statut de publication)
- `content.py` — value objects pour les contenus générés (annonce, post, script)

**Règle :** aucune dépendance vers `infrastructure/` ou `application/` ne doit entrer ici.
