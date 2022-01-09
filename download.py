import os
import json
from web3 import Web3, HTTPProvider

# Using web3py
url = "https://eth-mainnet.alchemyapi.io/v2/" + os.environ["ALCHEMY_KEY"]
web3 = Web3(HTTPProvider(url))


current_block = web3.eth.get_block('latest', True)
num = current_block['number']
most_recent_num = num
aggregate = {}

def make_serializable(val):
    val_type = type(val).__name__
    if val_type == "HexBytes":
        return val.hex()
    elif val_type == "list":
        return make_list_serializable(val)
    elif val_type == "dict":
        return make_dict_serializable(val)
    elif val_type == "AttributeDict":
        return make_serializable(val.__dict__)
    return val

def make_dict_serializable(data: dict):
    for key in data.keys():
        data[key] = make_serializable(data[key])
    return data

def make_list_serializable(data: list):
    return [make_serializable(val) for val in data]

current_block = make_serializable(current_block)

while num > most_recent_num - 5000:
    aggregate[num] = json.dumps(current_block)
    current_block = make_serializable(web3.eth.get_block(num - 1, True))
    num = num - 1
    print(f"{most_recent_num - num}/5000")

with open("data.json", "w") as file:
    json.dump(aggregate, file)


