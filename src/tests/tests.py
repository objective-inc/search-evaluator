
import os
import json
from dotenv import load_dotenv
import pytest

from objective_evaluator.evaluator import ObjectiveEvaluator
from objective_evaluator.scrapers.objective import ObjectiveScraper, ObjectiveScrapeParams
from objective_evaluator.scrapers.opensearch import OpenSearchScraper, OpenSearchScrapeParams
from objective_evaluator.scrapers.rest import RestScraper, RestScrapeParams
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

    def render_result(result):
        if isinstance(result, str):
            result = json.loads(result)
            print(json.dumps(result, indent=2))
            return f"""
                <div class="min-w-[200px]">
                    <h3 class="text-lg font-semibold mb-2">{result['prod_name']}</h3>
                    <div class="flex">
                        <div class="flex-none w-[100px] mr-2">
                            <img src="{result['image_url']}" alt="{result['prod_name']}" class="w-full">
                        </div>
                        <div class="flex-grow">
                            <p class="text-sm">
                                <span class="font-medium">Color:</span> {result['colour_group_name']}
                            </p>
                            <p class="text-sm">
                                <span class="font-medium">Department:</span> {result['department_name']}
                            </p>
                        </div>
                    </div>
                </div>
            """

    evaluator.comparison_html("comparison.html", render_result)



@pytest.mark.order(4)
def test_load_single_eval():
   evals = ["work/objective-10k_eval.json"]
   evaluator = ObjectiveEvaluator(scrapers=[], api_key='', work_dir="work/")
   evaluator.load_eval_results(evals)
   evaluator.summary()
   evaluator.full_results_html("full.html")

# @pytest.mark.order(5)
# def test_rest_scraper():

#     headers = {
#         "objective-index-ids": "idx_REDACTED"
#     }

#     query_params = {
#         "object_fields": "*"
#     }

#     params = RestScrapeParams(
#         base_url="http://localhost:8080/v1/indexes/idx_REDACTED",
#         endpoint="search",
#         query_param_name="query",
#         query_params=query_params,
#         limit=10,
#         headers=headers,
#         scrape_id="test-rest-scraper"

#     )

#     rest_scraper = RestScraper(params)
#     rest_scraper.scrape(["red dress", "graphic t-shirt"], save_to_path="work/rest_scrape.json")

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
