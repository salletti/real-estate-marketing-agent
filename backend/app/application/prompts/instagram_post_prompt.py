from langchain_core.prompts import PromptTemplate

_TEMPLATE = """\
Tu es un expert en marketing immobilier sur Instagram.

OBJECTIF :
Créer un post Instagram attractif et visuel pour promouvoir un bien immobilier.

DONNÉES :
- Type : {property_type}
- Sous-type : {sub_type}
- Ville : {city}
- Code postal : {postal_code}
- Pays : {country}
- Surface : {surface}
- Pièces : {rooms}
- Chambres : {bedrooms}
- Prix : {price}
- Charges : {charges}
- Taxes : {taxes}
- Description existante : {description}
- Équipements : {amenities}
- Balcons : {balcony_count}
- Terrasses : {terrace_count}
- État : {overall_condition}
- Travaux nécessaires : {work_required}
- Piscine : {has_pool}
- Parkings : {parking_count}
- Exposition : {exposures}
- Frais copropriété : {co_ownership_fee}
- Prestige : {is_prestige}

RÈGLES :
- Très court (max 3–4 lignes)
- Ton émotionnel et lifestyle : faire rêver, pas vendre
- Mettre en valeur le bien avec des mots évocateurs
- Ajouter des emojis pertinents et naturels
- Inclure 8 à 12 hashtags ciblés
- Ne jamais inventer d'informations
- Si une donnée est absente → ne pas la mentionner

FORMAT DE SORTIE OBLIGATOIRE :
{{
  "caption": "...",
  "hashtags": ["...", "..."]
}}

IMPORTANT :
- Aucun texte avant ou après le JSON
- JSON strict
- Pas de markdown\
"""


def build_instagram_post_prompt() -> PromptTemplate:
    return PromptTemplate.from_template(_TEMPLATE)
