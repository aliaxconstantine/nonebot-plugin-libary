from pydantic import BaseModel, Extra
GROUP_LIST = {}
L_MANGER_GROUP_ID = 897475157

class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
    L_MANGER_GROUP_ID = 897475157
