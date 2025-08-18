import click


class RPCUrl:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def __repr__(self):
        return f"<RPCUrl name={self.name!r} url={self.url!r}>"


class RPCUrlParamType(click.ParamType):
    name = "RPCUrl"

    def convert(self, value, param, ctx):
        if isinstance(value, RPCUrl):
            return value  # Already parsed from config
        if isinstance(value, str):
            # If CLI passes a plain URL, give it a default name
            return RPCUrl(name="custom", url=value)
        self.fail(f"Invalid RPC URL: {value}", param, ctx)


RPC_URL_TYPE = RPCUrlParamType()
