from typing import List

from pydantic import BaseModel


class PttPost(BaseModel):
    title: str
    link: str
    author: str


class PttResponse(BaseModel):
    status: str
    total_results: int
    posts: List[PttPost]
