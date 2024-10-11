import os
import webbrowser
from dotenv import load_dotenv
from objective_evaluator.evaluator import ObjectiveEvaluator
from objective_evaluator.scrapers.objective import ObjectiveScraper, ObjectiveScrapeParams
from objective_evaluator.scrapers.opensearch import OpenSearchScraper, OpenSearchScrapeParams


load_dotenv()

eval_api_key = os.getenv("OBJECTIVE_EVAL_API_KEY")
objective_api_key = os.getenv("OBJECTIVE_API_KEY")
objective_index_id = os.getenv("OBJECTIVE_INDEX_ID")


# Objective Scraper

objective_scraper = ObjectiveScraper(
    ObjectiveScrapeParams(
        limit=10,
        scrape_id="objective-quickstart",
        api_key=objective_api_key,
        index_id=objective_index_id,
        object_fields="*"
    )
)


# OpenSearch Scraper

query_template = {
    "query": {
        "multi_match": {
            "query": "{query}",
            "fields": ["prod_name^3", "detail_desc", "colour_group_name", "perceived_colour_master_name"] 
        }
    },
    "size": 10
}

opensearch_scraper = OpenSearchScraper(
    OpenSearchScrapeParams(
        limit=10,
        scrape_id="opensearch-quickstart",
        host="https://localhost",
        port=9200,
        username="admin",
        index="obj-quickstart",
        password=os.getenv("OPENSEARCH_INITIAL_ADMIN_PASSWORD"),
        query_template=query_template   
    )
)

evaluator = ObjectiveEvaluator(
    scrapers=[objective_scraper, opensearch_scraper],
    api_key=eval_api_key,
    work_dir="work/"
)

queries = [
    "red dress",
    "graphic t-shirt",
    "jeans for men",
    "blue blouse with buttons",
    "deep v-neck dress",
    "long sleeve shirt",
    "visible button fly jeans",
    "dropped shoulders top",
    "embroidery dress",
    "ladies flip-flops",
]

evaluator.run(queries, clear_work_dir=True)
evaluator.summary()
evaluator.comparison_html("quickstart_compare_results.html")
webbrowser.open('file://' + os.path.abspath("quickstart_compare_results.html"), new=2)
