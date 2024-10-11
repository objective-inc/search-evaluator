import os
import webbrowser
from dotenv import load_dotenv
from objective_evaluator.evaluator import ObjectiveEvaluator
from objective_evaluator.scrapers.objective import ObjectiveScraper, ObjectiveScrapeParams


load_dotenv()

eval_api_key = os.getenv("OBJECTIVE_EVAL_API_KEY")
objective_api_key = os.getenv("OBJECTIVE_API_KEY")
objective_index_id = os.getenv("OBJECTIVE_INDEX_ID")

objective_scraper = ObjectiveScraper(
    ObjectiveScrapeParams(
        limit=10,
        scrape_id="objective-quickstart",
        api_key=objective_api_key,
        index_id=objective_index_id,
        object_fields="*"
    )
)

evaluator = ObjectiveEvaluator(
    scrapers=[objective_scraper],
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
evaluator.full_results_html("quickstart_results.html")
webbrowser.open('file://' + os.path.abspath("quickstart_results.html"), new=2)


dataframes = evaluator.dfs
for df in evaluator.dfs:
    print(df.Name)
    print(df.head())
