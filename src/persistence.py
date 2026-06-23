import json
import os

class LocalPersistence:
    """Simulates localStorage using a local JSON file."""

    def __init__(self, filepath='data/local_storage.json'):
        self.filepath = filepath
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        self.data = self._load()

    def _load(self):
        # We check again if the file exists just before opening to be safe
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}

    def _save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f, indent=2)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self._save()

    def delete(self, key):
        if key in self.data:
            del self.data[key]
            self._save()
