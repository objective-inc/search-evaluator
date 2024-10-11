import json
from typing import List

import requests
from requests.auth import HTTPBasicAuth

from objective_evaluator.scraper import BaseScraper, ScrapeParams, SearchResults, SearchResultItem 

class OpenSearchScrapeParams(ScrapeParams):
    host: str
    port: int
    index: str
    username: str
    password: str
    ssl_verify: bool = False
    query_template: dict

class OpenSearchScraper(BaseScraper):

    def __init__(self, params: OpenSearchScrapeParams):
        super().__init__(params=params)
        self.params = params

    def scrape(self, queries: List[str], save_to_path: str) -> None:
        results = SearchResults(items=[])
        for query in queries:
            url = f"{self.params.host}:{self.params.port}/{self.params.index}/_search"
            payload = json.loads(json.dumps(self.params.query_template).replace('"{query}"', json.dumps(query)))        
            headers = {
                'Content-Type': 'application/json',
            }
            auth = HTTPBasicAuth(self.params.username, self.params.password)
            response = requests.post(
                url,
                json=payload,
                auth=auth,
                headers=headers,
                verify=self.params.ssl_verify
            )

            if response.status_code != 200:
                raise Exception(f"Failed to connect to OpenSearch API. Status code: {response.status_code}")
            
            hits = response.json().get('hits', {}).get('hits', [])
            for hit in hits[:self.params.limit]:
                results.items.append(SearchResultItem(
                    query=query,
                    object=hit['_source']
                ))

        with open(save_to_path, "w") as f:
            f.write(results.to_json())