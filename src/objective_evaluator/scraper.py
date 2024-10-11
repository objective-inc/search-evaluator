import json
from typing import List
from pydantic import BaseModel, RootModel, model_validator
from pydantic.dataclasses import dataclass



class ScrapeParams(BaseModel):
    limit: int
    scrape_id: str

class BaseScraper(BaseModel):
    params: ScrapeParams

    def __init__(self, params: ScrapeParams):
        super().__init__(params=params)

    def scrape(self, queries: List[str], save_to_path: str) -> None:
        raise NotImplementedError("Subclass must implement abstract method")


@dataclass
class SearchResultItem:
    query: str
    object: dict

@dataclass
class SearchResults:
    items: List[SearchResultItem]
    def to_json(self):
        return RootModel[List[SearchResultItem]](self.items).model_dump_json(indent=4)









    


# def to_json(data: SearchResults):
#     return RootModel[List[SearchResultItem]](data.items).model_dump_json(indent=4)
