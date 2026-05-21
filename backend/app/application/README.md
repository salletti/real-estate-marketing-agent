# application/

Ce dossier contient les **cas d'usage** (use cases) de l'application.

Chaque use case orchestre les entités du domaine et appelle les ports d'infrastructure.
Il ne connaît ni FastAPI ni les détails techniques des bases de données.

**Exemples futurs :**
- `generate_listing.py` — orchestration de la génération d'une annonce premium
- `generate_facebook_post.py` — génération d'un post Facebook
- `publish_content.py` — publication d'un contenu vers un canal externe

**Règle :** un use case dépend du domaine et des interfaces d'infrastructure, jamais de leur implémentation concrète.
