class Parameters:
    """
    Class that represents a set of parameters that can be accessed and modified. The parameters are stored in a dictionary and can be accessed and modified using the dot notation. The parameters can be loaded from environment variables with a specified prefix.
    """

    def __init__(self):
        super().__init__()

    def parse(self, data: dict):
        for key, value in data.items():
            subparams = type(self)()
            key: str = key.replace("-", "_")

            setattr(self, key, subparams)
            if isinstance(value, dict):
                subparams.parse(value)
            else:
                setattr(self, key, value)

    def from_env(self, *prefixes: list[str]):
        for prefix in prefixes:
            subparams_name: str = prefix.lower().strip("_")
            raw_attrs = dir(self)
            attrs = list(map(lambda str: str.lower(), raw_attrs))

            if subparams_name in attrs:
                subparams = getattr(self, raw_attrs[attrs.index(subparams_name)])
            else:
                subparams = type(self)()

            self._parse_env_vars(prefix, subparams)

            setattr(self, subparams_name, subparams)

    def _format_key(self, key, prefix):
        k = key.replace(prefix, "").lower()
        k = k.replace("_", " ").title().replace(" ", "")
        k = k[0].lower() + k[1:]
        return k

    def _convert(self, value: str):
        try:
            value = float(value)
        except ValueError:
            pass

        try:
            integer = int(value)
            if integer == value:
                value = integer

        except ValueError:
            pass

        return value

    def __repr__(self):
        return str(self.__dict__)
