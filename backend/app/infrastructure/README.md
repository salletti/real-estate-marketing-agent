# infrastructure/

Ce dossier contient les **adaptateurs techniques** : tout ce qui touche le monde extérieur.

Base de données, API tierces, systèmes de fichiers, files de messages — tout ici.

**Exemples futurs :**
- `llm/` — client Claude / OpenAI pour la génération de texte
- `facebook/` — client Graph API pour la publication
- `instagram/` — client pour les Reels
- `db/` — repositories PostgreSQL / SQLite
- `email/` — envoi d'emails via SMTP ou Resend

**Règle :** ce dossier implémente les interfaces définies dans `application/`.
Il ne doit pas contenir de logique métier.
