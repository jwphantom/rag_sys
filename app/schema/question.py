# build a schema using pydantic
from pydantic import BaseModel


class Question(BaseModel):
    canal: str
    prompt: str
    conversation: str
