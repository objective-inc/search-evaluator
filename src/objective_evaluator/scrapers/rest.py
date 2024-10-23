from typing import List, Dict, Any
import requests
from objective_evaluator.scraper import BaseScraper, ScrapeParams, SearchResults, SearchResultItem

class RestScrapeParams(ScrapeParams):
    base_url: str
    endpoint: str
    method: str = "GET"
    headers: Dict[str, str] = {}
    query_params: Dict[str, Any] = {}
    body: Dict[str, Any] = {}
    result_key: str = "results"
    inner_result_key: str = None
    query_param_name: str = "q"

class RestScraper(BaseScraper):
    def __init__(self, params: RestScrapeParams):
        super().__init__(params=params)
        self.params = params

    def scrape(self, queries: List[str], save_to_path: str) -> None:
        results = SearchResults(items=[])

        for query in queries:
            url = f"{self.params.base_url}/{self.params.endpoint}"
            
            query_params = self.params.query_params.copy()
            query_params[self.params.query_param_name] = query

            response = requests.request(
                method=self.params.method,
                url=url,
                headers=self.params.headers,
                params=query_params,
                json=self.params.body if self.params.method in ["POST", "PUT", "PATCH"] else None
            )

            response.raise_for_status()
            data = response.json()

            api_results = data.get(self.params.result_key, [])

            api_results = api_results[:self.params.limit]

            for result in api_results:
                results.items.append(SearchResultItem(
                    query=query,
                    object=result[self.params.inner_result_key] if self.params.inner_result_key is not None else result
                ))

        with open(save_to_path, "w") as f:
            f.write(results.to_json())
