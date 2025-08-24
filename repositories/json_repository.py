import json
import os
from typing import Dict, Any


class JsonRepository:
    @staticmethod
    def load_data(filename: str) -> Dict[str, Any]:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "..", "data", filename)
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_data(filename: str, data: Dict[str, Any]) -> None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "..", "data", filename)
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
