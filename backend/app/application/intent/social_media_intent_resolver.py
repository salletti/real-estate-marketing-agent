from typing import TypedDict


class SocialMediaIntent(TypedDict):
    generate_facebook: bool
    generate_instagram: bool


class SocialMediaIntentResolver:

    def resolve(self, input: str) -> SocialMediaIntent:
        lowered = input.lower()
        return SocialMediaIntent(
            generate_facebook="facebook" in lowered,
            generate_instagram="instagram" in lowered,
        )
