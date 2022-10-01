import json
from collections import Counter
from tkinter import Variable
import requests
import pandas as pd
import time
import os
from pathlib import Path
import utils as utils

w = utils.Write(Path(os.path.basename(__file__)).stem)

start_date = "2022-07-01"
variables = {"start_date": start_date, "limit": 10}


def get_from_hash(hash):
    print(hash)
    v = {"start_date": start_date, "tx_hash": hash}
    return utils.bitqueryAPICall(query_get_single_tx, v)


query_get_txs = """
query ($start_date: ISO8601DateTime, $limit: Int) { 
ethereum(network: avalanche) {
    transfers(
			options: {
				limit:$limit,
				# asc: "block.timestamp.time"
				asc: ["date.date"]
			}
			date: {since: $start_date}
			receiver:{is:"0x948011e8ca8df1e9c83fee88967a5fc30c7a604b"}
		) {
		transaction {hash}
    date {
		date
    }
   }
  }
}
"""
query_get_single_tx = """
query ($tx_hash: String) {
ethereum(network: avalanche) {
    transfers(
			txHash: {is:$tx_hash}
		) {
		transaction {hash}
		sender {address}
		receiver {address}
		amount
		# USD: amount(in:USD)
		currency {symbol, address}
		date {date}
   }
  }
}
"""


txs_result = utils.bitqueryAPICall(query_get_txs, variables)
print(txs_result)
transaction_hashes = []
for transfer in txs_result["data"]["ethereum"]["transfers"]:
    transaction_hashes.append(transfer["transaction"]["hash"])

# result = get_from_hash("0x264ccad32ca1dd61075fc6733fac64922ba271517c12ff8125d109c156fd48fd") # out
# result = get_from_hash("0x14a1fbec8135f1e1904d17df415c16488ad73589e5160170059ad63057ab0f06") # in

res = {}
calls_count = 0
curr_date = ""
delay = 70
for hash in transaction_hashes:
    print(curr_date)
    date = transfer["date"]["date"]
    if calls_count == 10:
        print("pausing for", delay, "seconds")
        time.sleep(delay)
        calls_count = 0
    result = get_from_hash(hash)
    in_or_out = ""
    amount = 0  # arUSD
    synth = ""
    print(result)
    for transfer in result["data"]["ethereum"]["transfers"]:
        curr_date = transfer["date"]["date"]
        if (
            transfer["receiver"]["address"] == "0x948011e8ca8df1e9c83fee88967a5fc30c7a604b"
            and transfer["currency"]["symbol"] == "arUSD"
        ):
            in_or_out = "in"
            amount += transfer["amount"]

        if (
            transfer["sender"]["address"] == "0x0000000000000000000000000000000000000000"
            and transfer["currency"]["symbol"] == "arUSD"
        ):
            in_or_out = "out"
            amount += transfer["amount"]
    for transfer in result["data"]["ethereum"]["transfers"]:
        if in_or_out == "in" and transfer["sender"]["address"] == "0x0000000000000000000000000000000000000000":
            synth = transfer["currency"]["symbol"]
        if in_or_out == "out" and transfer["receiver"]["address"] == "0x948011e8ca8df1e9c83fee88967a5fc30c7a604b":
            synth = transfer["currency"]["symbol"]
    if synth not in res:
        res[synth] = {"in": 0, "out": 0}
    res[synth][in_or_out] += amount
    calls_count += 1

print(res)
w.write_result(res)
w.write_to_csv(res)
