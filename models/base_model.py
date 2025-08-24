class BaseModel:

    def to_dict(self):
        return self._to_dict_recursive(self)

    def _to_dict_recursive(self, obj):
        if isinstance(obj, dict):
            return {k: self._to_dict_recursive(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._to_dict_recursive(item) for item in obj]
        elif hasattr(obj, "__dict__"):
            return self._to_dict_recursive(obj.__dict__)
        else:
            return obj
