class NoSuchLanguageError(Exception):
    def __init__(self, language):
        self.language = language

class NoSuchTranslationError(Exception):
    def __init__(self, language, key):
        self.language = language
        self.key = key
