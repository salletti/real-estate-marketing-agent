from langchain_core.prompts import PromptTemplate

_TEMPLATE = """\
Tu es un expert en marketing immobilier sur les réseaux sociaux.

OBJECTIF :
Créer un post Facebook attractif et engageant pour promouvoir un bien immobilier.

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
- Ton émotionnel, chaleureux et humain
- Court et impactant (max 5 lignes)
- Mettre en avant 2 ou 3 points forts maximum
- Inclure un call-to-action clair en fin de post
- Ne jamais inventer d'informations
- Si une donnée est absente → ne pas la mentionner
- Les hashtags doivent être pertinents et ciblés (5 à 8 maximum)

FORMAT DE SORTIE OBLIGATOIRE :
{{
  "post": "...",
  "hashtags": ["...", "..."]
}}

IMPORTANT :
- Aucun texte avant ou après le JSON
- JSON strict
- Pas de markdown\
"""


def build_facebook_post_prompt() -> PromptTemplate:
    return PromptTemplate.from_template(_TEMPLATE)
