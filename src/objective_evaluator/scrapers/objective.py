from typing import List
from objective import Objective
from objective_evaluator.scraper import BaseScraper, ScrapeParams, SearchResults, SearchResultItem

class ObjectiveScrapeParams(ScrapeParams):
    api_key: str
    index_id: str
    object_fields: str

class ObjectiveScraper(BaseScraper):
    def __init__(self, params: ObjectiveScrapeParams):
        super().__init__(params=params)
        self.params = params
    
    def scrape(self, queries: List[str], save_to_path: str) -> None:
        results = SearchResults(items=[])
        client = Objective(api_key=self.params.api_key)

        for query in queries:
            resp = client.indexes.search(
                index_id=self.params.index_id,
                query=query,
                limit=self.params.limit,
                object_fields=self.params.object_fields
            )
            for result in resp.results:
                results.items.append(SearchResultItem(
                    query=query,
                    object=result.object
                ))
        with open(save_to_path, "w") as f:
            f.write(results.to_json())