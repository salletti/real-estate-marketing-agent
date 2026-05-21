# agents/

Ce dossier contiendra les **agents IA** du projet.

Un agent est une entité autonome capable de décider quels outils appeler, dans quel ordre,
pour accomplir un objectif défini (ex : générer et publier tous les contenus d'un bien).

**Exemples futurs :**
- `marketing_agent.py` — agent principal de génération de contenus
- `tools/` — tools exposés à l'agent (generate_listing, post_to_facebook, etc.)

**Compatibilité MCP future :**
Les tools définis ici pourront être exposés comme des ressources MCP (Model Context Protocol),
permettant à n'importe quel client compatible MCP d'appeler ces capacités directement.

**Règle :** les agents orchestrent les use cases de `application/`.
Ils ne contiennent pas de logique métier directe.
