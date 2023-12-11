class AttrDict(dict):
    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def _batch_convert_to_attr_dict(l: list) -> list:
    return [_convert_to_attr_dict(item) if type(item) is dict else item for item in l]


def _convert_to_attr_dict(d: dict) -> AttrDict:
    result = AttrDict()
    for k in d:
        v = d[k]
        if type(v) is dict:
            v = _convert_to_attr_dict(v)
        elif type(v) is list:
            v = _batch_convert_to_attr_dict(v)
        result[k] = v
    return result


def _load_config() -> AttrDict:
    import yaml

    with open("config.yaml", "r") as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
        cfg = _convert_to_attr_dict(cfg)
    return cfg


def get_channel_user_id(channel: str, user: str) -> str:
    return f"c:{channel}_u:{user}"


cfg = _load_config()
