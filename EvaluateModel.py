from urllib.request import AbstractBasicAuthHandler

from deepeval.test_case import LLMTestCase
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.metrics.faithfulness import FaithfulnessTemplate

import utils
import chains

class CustomTemplate(FaithfulnessTemplate):
    @staticmethod
    def generate_claims(actual_output: str):
        return f"""
        Based on the given text, please extracta comprehensive list of facts that can inferred
        from a provided text.

        While you process the text, please ignore the following keywords:"祝你有個美好的一天!", 
        "謝謝你的提問", "最後 祝您 平安快樂" and "希望我的回答有幫助到你。"

        Example:
        Example Text:
        "CNN claims that the sun is 3 times smaller than earth"
        Example JSON:
        {{
        "claims":[]
        }}
        ======== END OF EXAMPLE ========

        Text:
        {actual_output}
        JSON:
        """


open_ai_key = utils.get_secret("OPENAI_API_KEY")

suggestion = chains.get_suggestion_chain("覺得腿部肌肉酸痛怎麼辦?")

source_documents = suggestion.get("source_documents")
retrieval_context = []
for doc in source_documents:
    retrieval_context.append(doc.metadata.get("answer", ""))

for context in retrieval_context:
    print("----------")
    print(f"Context: {context}")
    print("----------")

test_case = LLMTestCase(
    input="覺得腿部肌肉酸痛怎麼辦?",
    actual_output=suggestion.get("result"),
    # expected_output="在台灣勞工工作滿半年後,根據《勞動基準法》的規定，應享有3天的特休假。",
    # retrieval_context=[
    #     "根據《勞動基準法》的規定，台灣勞工工作滿半年後,應享有3天的特休假。",
    #     "根據《勞動基準法》的規定，台灣勞工工作滿一年後,應享有一個禮拜的特休假",
    #     "根據《勞動基準法》的規定，台灣勞工工作滿兩年後,應享有十天的特休假"
    # ]
    retrieval_context=retrieval_context
)

metric = FaithfulnessMetric(
    threshold = 0.5,
    model = "gpt-5.4",
    include_reason=True,
    evaluation_template=CustomTemplate
)

test_results = evaluate(metrics = [metric], test_cases = [test_case]).test_results
for result in test_results:
    for metric_data in result.metrics_data: 
        print("----------")
        print(f"Metric: {metric_data.name}")
        print(f"Score: {metric_data.score}")
        print(f"Reason: {metric_data.reason}")
        print("----------")
