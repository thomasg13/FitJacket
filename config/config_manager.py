import os

class ConfigurationManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigurationManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        # Load from environment variables
        self._config = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "STRAVA_CLIENT_ID": os.getenv("STRAVA_CLIENT_ID"),
            "STRAVA_CLIENT_SECRET": os.getenv("STRAVA_CLIENT_SECRET"),
            "STRAVA_REDIRECT_URI": os.getenv("STRAVA_REDIRECT_URI"),
        }

    def get(self, key, default=None):
        return self._config.get(key, default)