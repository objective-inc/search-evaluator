
import json
import time
import requests
from pydantic import BaseModel 

class EvaluationParams(BaseModel):
    scrape_results_path: str
    save_to_path: str
    api_key: str
    eval_name: str
    

class ObjectiveAntonEvalFailed(Exception):
    """Custom exception for ObjectiveAntonEvaluator failures."""
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ObjectiveEvalRunner(BaseModel):
    params: EvaluationParams

    def __init__(self, params: EvaluationParams):
        super().__init__(params=params)

    def run(self) -> str:
        # Load the crawl results
        with open(self.params.scrape_results_path, 'r') as f:
            scrape_results = json.load(f)

        payload = {
            "configuration": {
                "eval_name": self.params.eval_name
            },
            "data": scrape_results
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.params.api_key}"
        }

        response = requests.post(
            "https://api.objective.inc/v1/evaluations",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            evaluation_result = response.json()
            eval_id = evaluation_result["id"]
            status = self.status(eval_id)
            while status['status'] in ["processing", "accepted"]:
                time.sleep(1)
                status = self.status(eval_id)

            if status['status'] == "failed":
                raise ObjectiveAntonEvalFailed(
                    f"Evaluation failed. Status code: {response.status_code}, Response: {response.text}",
                    response.status_code
                )
            elif status['status'] == "error":
                raise ObjectiveAntonEvalFailed(
                    f"Evaluation failed. Status code: {response.status_code}, Response: {response.text}",
                    response.status_code
                )
            elif status['status'] == "completed":
                # Save the results to the specified path
                with open(self.params.save_to_path, 'w') as f:
                    json.dump(status, f, indent=4)
            
            return eval_id
        else:
            raise ObjectiveAntonEvalFailed(
                f"Request failed with status code {response.status_code}",
                response.status_code
            )
        

    def status(self, eval_id: str):
        headers = {
            "Authorization": f"Bearer {self.params.api_key}"
        }
        response = requests.get(
            f"https://api.objective.inc/v1/evaluations/{eval_id}",
            headers=headers
        )
        return response.json()
