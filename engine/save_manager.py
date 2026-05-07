import json
from pathlib import Path

class SaveManager:
    def __init__(self, path='saves/save.json'):
        self.path = Path(path)

    def save(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def load(self):
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding='utf-8'))
