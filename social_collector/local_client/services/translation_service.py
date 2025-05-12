from langdetect import detect, DetectorFactory
import argostranslate.translate
import warnings

DetectorFactory.seed = 0

SIMILAR_LANGUAGES = {"ru", "uk", "be", "bg", "mk"}

class translation_service:
    _instance = None

    @staticmethod
    def get_instance():
        return translation_service()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(translation_service, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._load_installed_languages()

    def _load_installed_languages(self):
        self.installed_languages = argostranslate.translate.get_installed_languages()
        self.ru_lang = next((lang for lang in self.installed_languages if lang.code == "ru"), None)
        self.en_lang = next((lang for lang in self.installed_languages if lang.code == "en"), None)
        if not self.ru_lang or not self.en_lang:
            raise RuntimeError("Russian and/or English language models are not installed.")
        self.translator = self.ru_lang.get_translation(self.en_lang)

    def translate(self, text):
        try:
            lang = detect(text)
        except Exception as e:
            warnings.warn(f"[WARNING] Language detection failed: {e}")
            return None

        token_count = len(text.strip().split())

        if lang == "ru":
            try:
                return self.translator.translate(text)
            except Exception as e:
                warnings.warn(f"[WARNING] Translation failed: {e}")
                return None
        elif lang in SIMILAR_LANGUAGES and token_count < 7:
            try:
                return self.translator.translate(text)
            except Exception as e:
                warnings.warn(f"[WARNING] Translation failed: {e}")
                return None
        elif lang == "en":
            return text
        else:
            warnings.warn(f"[WARNING] Unsupported language detected: {lang}")
            return None
