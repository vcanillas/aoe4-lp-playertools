import pickle
import os
from typing import Dict, Any


class PickleRepository:
    @staticmethod
    def load_data(filename: str) -> Dict[str, Any]:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "..", "data", filename)
        with open(data_path, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def save_data(filename: str, data: Dict[str, Any]) -> None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "..", "data", filename)
        with open(data_path, "wb") as f:
            pickle.dump(data, f)
