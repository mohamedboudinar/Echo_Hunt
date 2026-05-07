import json
from pathlib import Path


class HighScoreManager:
    def __init__(self, path="saves/high_scores.json", limit=8):
        self.path = Path(path)
        self.limit = limit

    def load(self):
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        if not isinstance(data, list):
            return []
        return data

    def add_score(self, player_name, max_level, survival_time):
        scores = self.load()
        scores.append(
            {
                "name": player_name.strip() or "PLAYER",
                "max_level": int(max_level),
                "survival_time": round(float(survival_time), 1),
            }
        )
        scores.sort(key=lambda item: (item["max_level"], item["survival_time"]), reverse=True)
        scores = scores[: self.limit]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(scores, indent=2), encoding="utf-8")
        return scores
