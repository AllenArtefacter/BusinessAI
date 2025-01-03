# import logging
# import os
# from typing import Dict, List
#
# import pandas as pd
# from tqdm import tqdm
#
# from src.chat.chat import Chat, Message
# from src.database.old.pymysql_wrapper import MySQLWrapper
# from src.models.gpt_chat_completion import GPTChatCompletion
# from src.prompt_engineering import PromptConfig, sql_documentation_generator
# from src.tools.utils import extract_sql
#
# logger = logging.getLogger(__name__)
#
# logger.setLevel(logging.DEBUG)
#
#
# class PromptEvaluator:
#     def __init__(
#         self,
#         model,
#         prompts: List[PromptConfig],
#         requests: List[str],
#         ideal_sql_answers: List[str],
#         expected_results: List[pd.DataFrame],
#         db: MySQLWrapper,
#         iterations: int = 2,
#     ):
#         self.model = model
#         self.prompts = prompts
#         self.requests = requests
#         self.ideal_sql_answers = ideal_sql_answers
#         self.expected_results = expected_results
#         self.db = db
#         self.results = None
#         self.iterations = iterations
#
#     def run(self, **kwargs):
#         logger.info("Reset Results")
#         self.results = None
#
#         pgb = tqdm(total=self.iterations * len(self.prompts) * len(self.requests))
#         for i in range(self.iterations):
#             logger.info(f"Running Iteration: {i}")
#             self.run_iteration(iteration=i, pgb=pgb, **kwargs)
#
#     def run_iteration(self, **kwargs):
#         for prompt in self.prompts:
#             logger.info(f"Running Prompt: {prompt}")
#             self.run_prompt(prompt, **kwargs)
#
#     def run_prompt(self, prompt, **kwargs):
#         for request in self.requests:
#             logger.info(f"Running Request: {request}")
#             self.run_request(prompt, request, **kwargs)
#
#     def run_request(self, prompt, request, pgb, run_sql: bool = False, **kwargs):
#         chat = Chat.from_message(Message.from_user(request, *prompt(request)))
#         logger.debug(f"Chat to predict: {chat}")
#         completion = self.model.predict(chat)
#         logger.debug(f"Completion: {completion}")
#         self.save_completion_result(prompt, request, completion, **kwargs)
#         # update progress bar pgb
#         if run_sql:
#             self.run_sql_on_last_results()
#         pgb.update(1)
#
#     def save_completion_result(self, prompt, request, completion, iteration):
#         if self.results is None:
#             self.results = pd.DataFrame(
#                 columns=[
#                     "prompt",
#                     "request",
#                     "completion",
#                     "iteration",
#                     "sql_code",
#                     "sql_result",
#                     "sql_error",
#                 ]
#             )
#
#         new_row = pd.DataFrame(
#             {
#                 "prompt": [prompt],
#                 "request": [request],
#                 "completion": [completion],
#                 "iteration": [iteration],
#                 "sql_code": [None],
#                 "sql_result": [None],
#                 "sql_error": [None],
#             }
#         )
#
#         self.results = pd.concat([self.results, new_row], ignore_index=True)
#
#     def run_sql_on_last_results(self):
#         last_row, i = self.results.iloc[-1], self.results.index[-1]
#
#         code, _ = extract_sql(last_row["completion"])
#         self.results.at[i, "sql_code"] = code
#         try:
#             logging.info(f"Running SQL query: {code}")
#             self.results.at[i, "sql_result"] = self.db.fetch_results_pandas(code)
#         except pd.errors.DatabaseError as e:
#             self.results.at[i, "sql_error"] = str(e)
#
#     def evaluate_query(self, prompt: str, request: str, ideal_sql: str) -> float:
#         correct_predictions = 0
#         total_predictions = 10
#
#         for _ in range(total_predictions):
#             generated_sql = self.model.generate_sql(prompt, request)
#             if self.compare_sql(generated_sql, ideal_sql):
#                 correct_predictions += 1
#
#         return correct_predictions / total_predictions
#
#     def evaluate(self) -> Dict[str, Dict[str, float]]:
#         results = {}
#
#         for prompt in self.prompts:
#             prompt_results = {}
#
#             for i, request in enumerate(self.requests):
#                 ideal_sql = self.ideal_sql_answers[i]
#                 expected_result, expected_columns = self.expected_results[i]
#
#                 query_accuracy = self.evaluate_query(prompt, request, ideal_sql)
#                 result_accuracy = self.evaluate_result(
#                     prompt, request, expected_result, expected_columns
#                 )
#
#                 prompt_results[request] = {
#                     "query_accuracy": query_accuracy,
#                     "result_accuracy": result_accuracy,
#                 }
#
#             results[prompt] = prompt_results
#
#         return results
#
#     def evaluate_result(
#         self,
#         prompt: str,
#         request: str,
#         expected_result: pd.DataFrame,
#         expected_columns: List[str],
#     ) -> float:
#         correct_predictions = 0
#         total_predictions = 10
#
#         for _ in range(total_predictions):
#             generated_sql = self.model.generate_sql(prompt, request)
#             result_df = self.db.fetch_results_pandas(generated_sql)
#
#             if self.compare_results(result_df, expected_result, expected_columns):
#                 correct_predictions += 1
#
#         return correct_predictions / total_predictions
#
#     @staticmethod
#     def compare_sql(generated_sql: str, ideal_sql: str) -> bool:
#         # Implement your logic to compare generated_sql with ideal_sql
#         # Return True if they are the same, False otherwise
#         pass
#
#     @staticmethod
#     def compare_results(
#         generated_result: pd.DataFrame,
#         expected_result: pd.DataFrame,
#     ) -> bool:
#         matching_columns = [
#             col for col in expected_result.columns if col in generated_result.columns
#         ]
#
#         if not expected_result.loc[:, matching_columns].equals(
#             generated_result.loc[:, matching_columns]
#         ):
#             return False
#
#         return True
#
#
# from evaluation.samples import best_seller, doh, sell_out_qty
#
# if __name__ == "__main__":
#     db = MySQLWrapper(
#         host=os.environ["DB_HOST"],
#         user=os.environ["DB_USERNAME"],
#         password=os.environ["DB_PASSWORD"],
#         database=os.environ["DB_NAME"],
#     )
#     columns = db.get_table_info()
#
#     prompts: List[PromptConfig] = [
#         i(db.sql_dialect, sql_documentation_generator(columns))
#         for i in [
#             # PromptConfig.no_prompt,
#             PromptConfig.only_code,
#             PromptConfig.think_about_it,
#         ]
#     ]
#
#     requests = ["What is my best seller?"]
#
#     correct_sql_queries = [
#         doh.query,
#         sell_out_qty.query,
#         best_seller.query,
#     ]
#
#     y_df = [db.fetch_results_pandas(query) for query in correct_sql_queries]
#
#     model = GPTChatCompletion(os.environ["OPENAI_API_KEY"], model="gpt-3.5-turbo")
#
#     pe = PromptEvaluator(
#         model=model,
#         prompts=prompts,
#         requests=requests,
#         ideal_sql_answers=correct_sql_queries,
#         expected_results=y_df,
#         db=db,
#     )
#     pe.run(run_sql=True)
#     print(pe.results)
