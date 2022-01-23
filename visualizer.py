from graph import *
import json

transactions = set()

with open("data.json", "r") as file:
    data = json.load(file)

    for _, block in data.items():
        block = json.loads(block)
        for transaction in block['transactions']:
            sender = Wallet(transaction['from'])
            recipient = Wallet(transaction['to'])
            transactions.add(
                Transaction(
                    sender,
                    recipient,
                    float(transaction['value'])/(10**18),
                    transaction['nonce'],
                    block['number']
                )
            )

g = Graph([], transactions)

g.visualize()
