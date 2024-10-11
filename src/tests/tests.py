
import os
from dotenv import load_dotenv
import pytest

from objective_evaluator.evaluator import ObjectiveEvaluator
from objective_evaluator.scrapers.objective import ObjectiveScraper, ObjectiveScrapeParams
from objective_evaluator.scrapers.opensearch import OpenSearchScraper, OpenSearchScrapeParams

load_dotenv()


@pytest.mark.order(1)
def test_opensearch_scraper():
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
            scrape_id="Test Opensearch Evaluation",
            index="obj-quickstart",
            host="https://localhost",
            port=9200,
            username="admin",
            password=os.getenv("OPENSEARCH_INITIAL_ADMIN_PASSWORD"),
            query_template=query_template
        )
    )
    opensearch_scraper.scrape(["red dress", "graphic t-shirt"], save_to_path="work/opensearch_scrape.json")


@pytest.mark.order(2)
def test_objective_scraper():
    objective_scraper = ObjectiveScraper(
        ObjectiveScrapeParams(
            limit=10,
            scrape_id="Test Objective Evaluation",
            api_key=os.getenv("OBJECTIVE_EVAL_API_KEY"),
            index_id=os.getenv("OBJECTIVE_INDEX_ID"),
            object_fields="*"
        )
    )
    objective_scraper.scrape(["red dress", "graphic t-shirt"], save_to_path="work/objective_scrape.json")

@pytest.mark.order(3)
def test_load_compare_evals():
    evals = ["work/objective-10k_eval.json", "work/opensearch-10k_eval.json"]
    evaluator = ObjectiveEvaluator(scrapers=[], api_key='', work_dir="work/")
    evaluator.load_eval_results(evals)
    df = evaluator.comparison_html("comparison.html")



@pytest.mark.order(4)
def test_load_single_eval():
   evals = ["work/objective-10k_eval.json"]
   evaluator = ObjectiveEvaluator(scrapers=[], api_key='', work_dir="work/")
   evaluator.load_eval_results(evals)
   evaluator.summary()
   evaluator.full_results_html("full.html")

@pytest.mark.order(2)
def test_evaluator():

    eval_api_key = os.getenv("OBJECTIVE_EVAL_API_KEY")

    objective_api_key = os.getenv("OBJECTIVE_API_KEY")
    objective_index_id = os.getenv("OBJECTIVE_INDEX_ID")

    objective_scraper = ObjectiveScraper(
        ObjectiveScrapeParams(
            limit=10,
            scrape_id="objective-10k",
            api_key=objective_api_key,
            index_id=objective_index_id,
            object_fields="*"
        )
    )

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
            scrape_id="opensearch-10k",
            index="obj-quickstart",
            host="https://localhost",
            port=9200,
            username="admin",
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
