import json
import os
import shutil
import concurrent.futures

from typing import Any, Dict, List

import pandas as pd
from pydantic import BaseModel, ConfigDict

from objective_evaluator.evalrunner import EvaluationParams, ObjectiveEvalRunner
from objective_evaluator.scraper import BaseScraper


DF_STYLE = [
                {'selector': 'th', 'props': [('background-color', '#f2f2f2'), ('color', 'black'), ('font-weight', 'bold')]},
                {'selector': 'td', 'props': [('border', '1px solid #ddd'), ('padding', '8px')]},
                {'selector': 'tr:nth-of-type(even)', 'props': [('background-color', '#f9f9f9')]},
            ]

HTML_TEMPLATE = """
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ text-align: left; padding: 8px; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1><svg class="text-primary fill-current h-5 w-auto" width="93" height="30" viewBox="0 0 93 30" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="31.8769" width="29.9999" height="29.9999" fill="currentColor"></rect><path d="M92.8086 30L62.8087 30L92.8086 8.01086e-05L92.8086 30Z" fill="currentColor"></path><ellipse cx="15" cy="15" rx="15" ry="15" fill="currentColor"></ellipse></svg>&nbsp;&nbsp;{title}</h1>
        {df_html}
    </body>
    </html>
    """ 


class ObjectiveEvaluator(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True
        )
    scrapers: List[BaseScraper]
    api_key: str
    work_dir: str
    dfs: List[pd.DataFrame]

    def __init__(self, scrapers: List[BaseScraper], api_key: str, work_dir: str):
        super().__init__(scrapers=scrapers, api_key=api_key, work_dir=work_dir, dfs=[])
        self.api_key = api_key
        self.work_dir = work_dir

    def run(self, queries: List[str], clear_work_dir: bool = False) -> None:
        if clear_work_dir: 
            if os.path.exists(self.work_dir):
                shutil.rmtree(self.work_dir)
            os.makedirs(self.work_dir)
        completed_eval_paths = []

        def process_scraper(scraper, queries):
            scrape_path = self.work_dir + scraper.params.scrape_id + ".json"
            eval_path = scrape_path.replace(".json", "_eval.json")
            scraper.scrape(queries, scrape_path)
            eval_id = ObjectiveEvalRunner(
                EvaluationParams(
                    scrape_results_path=scrape_path,
                    save_to_path=eval_path,
                    api_key=self.api_key,
                    eval_name=scraper.params.scrape_id + "_eval"
                )
            ).run()
            print("Evaluation ID completed: ", eval_id)
            return eval_path

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_scraper, scraper, queries) for scraper in self.scrapers]
            completed_eval_paths = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        self.load_eval_results(completed_eval_paths)


    def eval_to_df(self, path: str) -> pd.DataFrame:
        with open(path, 'r') as file:
            data = json.load(file)
        
        judgements = data.get('judgements', [])
        rows = []
        
        current_query = None
        position = 0
        for judgement in judgements:
            if judgement['query'] != current_query:
                current_query = judgement['query']
                position = 1
            else:
                position += 1
            
            row = {
                'query': judgement['query'],
                'position': position,
                'object_id': judgement['object_id'],
                'object': json.dumps(judgement['object']),  # Convert object to JSON string
                'score': judgement['judgement']['score'],
                'label': judgement['judgement']['label'],
                'explanation': judgement['judgement']['explanation']
            }
            rows.append(row)
        df = pd.DataFrame(rows)
        df.Name = path.split("/")[-1].replace("_eval.json", "") 
        return df
            

    def load_eval_results(self, paths: List[str]):
        for path in paths:
            df = self.eval_to_df(path)
            self.dfs.append(df)



    def summary(self):
        for df in self.dfs:
            judgement_counts = df['label'].value_counts()
            print(f"Summary for {df.Name}:")
            print(f"GREAT: {judgement_counts.get('GREAT', 0)}")
            print(f"OK: {judgement_counts.get('OK', 0)}")
            print(f"BAD: {judgement_counts.get('BAD', 0)}")
            print()  # Add a blank line between summaries



    def full_results_html(self, save_to_path: str):
        for df in self.dfs:
            styled_df = df.style.set_table_styles(DF_STYLE)
            full_html = styled_df.to_html()

            # Generate summary section
            summary_html = "<h2>Summary</h2>"
            summary_html += "<table>"
            summary_html += "<tr><th>Label</th><th>Count</th><th>Percentage</th></tr>"
            total_judgements = len(df)
            for label in ['GREAT', 'OK', 'BAD']:
                count = df['label'].value_counts().get(label, 0)
                percentage = (count / total_judgements) * 100 if total_judgements > 0 else 0
                summary_html += f"<tr><td>{label}</td><td>{count}</td><td>{percentage:.2f}%</td></tr>"
            summary_html += "</table>"

            # Add summary section to the full HTML
            full_html = summary_html + full_html

            html = HTML_TEMPLATE.format(title="Evaluation Results - " + df.Name, df_html=full_html)
            with open(save_to_path, "w") as f:
                f.write(html)


    def comparison_df(self):
        if len(self.dfs) < 2:
            raise ValueError("At least two DataFrames are required to join.")
        result_df = self.dfs[0][['query', 'position', 'label', 'object', 'explanation']].copy()
        result_df.columns = ['query', 'position', f'{self.dfs[0].Name}_label', f'{self.dfs[0].Name}_object', f'{self.dfs[0].Name}_explanation']
        
        for df in self.dfs[1:]:
            temp_df = df[['query', 'position', 'label', 'object', 'explanation']].copy()
            temp_df.columns = ['query', 'position', f'{df.Name}_label', f'{df.Name}_object', f'{df.Name}_explanation']
            result_df = pd.merge(result_df, temp_df, on=['query', 'position'], how='outer')
        
        return result_df.sort_values(['query', 'position']).reset_index(drop=True)
       
    def comparison_html(self, save_to_path: str):
        df = self.comparison_df()
        styled_df = df.style.set_table_styles(DF_STYLE)

        # Generate summary section
        summary_html = "<h2>Summary Comparison</h2>"
        summary_html += "<table>"
        summary_html += "<tr><th>Eval Name</th><th>GREAT</th><th>OK</th><th>BAD</th><th>Total</th></tr>"

        for df in self.dfs:
            total_judgements = len(df)
            great_count = df['label'].value_counts().get('GREAT', 0)
            ok_count = df['label'].value_counts().get('OK', 0)
            bad_count = df['label'].value_counts().get('BAD', 0)

            summary_html += f"<tr>"
            summary_html += f"<td>{df.Name}</td>"
            summary_html += f"<td>{great_count} ({great_count/total_judgements*100:.2f}%)</td>"
            summary_html += f"<td>{ok_count} ({ok_count/total_judgements*100:.2f}%)</td>"
            summary_html += f"<td>{bad_count} ({bad_count/total_judgements*100:.2f}%)</td>"
            summary_html += f"<td>{total_judgements}</td>"
            summary_html += f"</tr>"

        summary_html += "</table>"

        full_html = summary_html + styled_df.to_html()

        html = HTML_TEMPLATE.format(title="Evaluation Comparison", df_html=full_html)
        with open(save_to_path, "w") as f:
            f.write(html)

