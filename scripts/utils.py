import json
import requests
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os.path

API_KEY = None
if os.path.isfile('.env'):
    load_dotenv()
    API_KEY = os.getenv('API_KEY')

now = datetime.now()  # current date and time
date_time = now.strftime("%Y-%m-%d")


def df(data, columns=None):
    df = pd.DataFrame(data)
    if columns:
        df.columns = columns
    return df


class Write:
    def __init__(self, basename):
        self.basename = basename
        path = os.path.join("output", self.basename)
        os.makedirs(path, exist_ok=True)
        self.output_file_basename = os.path.join(
            path, ' '.join([date_time, self.basename]))

    def write_result(self, data):
        name = self.output_file_basename + ".json"
        with open(name, "w") as f:
            json.dump(data, f)

    def write_to_csv(self, data):
        name = self.output_file_basename + ".csv"
        df = df(data)
        df.to_csv(name, encoding="utf-8", index=False)


def bitqueryAPICall(query: str, variables: dict = {}, api_key: str = None):
    if not api_key:
        api_key = API_KEY
    headers = {"X-API-KEY": api_key}
    request = requests.post("https://graphql.bitquery.io/",
                            json={
                                "query": query,
                                "variables": variables
                            },
                            headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed and return code is {}.      {}".format(
            request.status_code, query))
