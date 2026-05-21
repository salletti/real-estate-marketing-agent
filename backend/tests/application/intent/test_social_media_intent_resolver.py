from app.application.intent.social_media_intent_resolver import SocialMediaIntentResolver


class TestSocialMediaIntentResolver:

    def setup_method(self):
        self.resolver = SocialMediaIntentResolver()

    def test_facebook_only(self):
        intent = self.resolver.resolve("Génère un post Facebook")
        assert intent["generate_facebook"] is True
        assert intent["generate_instagram"] is False

    def test_instagram_only(self):
        intent = self.resolver.resolve("Génère un post Instagram")
        assert intent["generate_facebook"] is False
        assert intent["generate_instagram"] is True

    def test_both_platforms(self):
        intent = self.resolver.resolve("Génère Facebook et Instagram")
        assert intent["generate_facebook"] is True
        assert intent["generate_instagram"] is True

    def test_no_platform(self):
        intent = self.resolver.resolve("Génère un post immobilier")
        assert intent["generate_facebook"] is False
        assert intent["generate_instagram"] is False

    def test_facebook_uppercase(self):
        intent = self.resolver.resolve("FACEBOOK post")
        assert intent["generate_facebook"] is True

    def test_instagram_mixed_case(self):
        intent = self.resolver.resolve("InStaGrAm story")
        assert intent["generate_instagram"] is True
