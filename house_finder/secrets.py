class KeysExhaustedError(RuntimeError):
    pass


class Secret:

    def __init__(self, keys):
        self.available_keys = keys
        self.used_keys = []
        self.rotate()

    def rotate(self):
        if hasattr(self, 'key'):
            self.used_keys.append(self.key)

        try:
            self.key = self.available_keys.pop(0)
        except IndexError:
            raise KeysExhaustedError()

    @classmethod
    def from_config(cls, config):
        if 'api_key' in config:
            return cls([config['api_key']])
        else:
            return cls(config['api_keys'])


class Secrets:

    @classmethod
    def from_config(cls, config):
        return {
            k: Secret.from_config(v)
            for k, v in config.items()
        }
