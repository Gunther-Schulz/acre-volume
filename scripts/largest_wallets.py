import os
from pathlib import Path
import scripts.utils as utils

w = utils.Write(Path(os.path.basename(__file__)).stem)

query = """
query ($start_date: ISO8601DateTime) {
ethereum(network: avalanche) {
    transfers(
			options: {
				limit:100000,
				desc: ["amount"]
			}
			date: {since: $start_date}
			receiver:{not:"0xc768915863a333db9bb871bd687dd0a0ae41a3be"}
			sender:{is:"0x0000000000000000000000000000000000000000"}
			currency: {is: "0x025AB35fF6AbccA56d57475249baaEae08419039"}
		) {
		receiver {address}
		amount
		currency {symbol, address}
   }
  }
}
"""

start_date = "2022-07-01"
query_variables = {"start_date": start_date}

result = utils.bitqueryAPICall(query, query_variables)
output = []
for r in result["data"]["ethereum"]["transfers"]:
    output.append([r["receiver"]["address"], r["amount"]])


w.write_result(result)
w.write_to_csv(output)
# print(result)
