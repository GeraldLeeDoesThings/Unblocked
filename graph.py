from __future__ import annotations
import queue
from typing import *


class Wallet:

    def __init__(self, address: str, transactions: Optional[Iterable[Transaction]] = None):
        self.address = address
        self.transactions = set() if transactions is None \
            else set(filter(lambda t: t.adjacent_to(self), transactions))

    def get_transactions_out(self) -> Set[Transaction]:
        return set(filter(lambda t: t.sender == self, self.transactions))

    def get_transactions_in(self) -> Set[Transaction]:
        return set(filter(lambda t: t.recipient == self, self.transactions))

    def process_transaction(self, transaction: Transaction) -> Wallet:
        if transaction.adjacent_to(self):
            self.transactions.add(transaction)
        return self

    def __eq__(self, other) -> bool:
        if isinstance(other, Wallet):
            return other.address == self.address
        return False

    def __hash__(self):
        return self.address


class Transaction:

    def __init__(self, sender: Wallet, recipient: Wallet, amount: float, nonce: int, block: int):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.nonce = nonce
        self.block = block

    def adjacent_to(self, to: Wallet):
        return self.sender == to or self.recipient == to

    def __eq__(self, other) -> bool:
        if isinstance(other, Transaction):
            return other.nonce == self.nonce
        return False

    def __hash__(self):
        return self.nonce


class Graph:

    def __init__(self, wallets: Iterable[Wallet], transactions: Iterable[Transaction]):
        self.wallets = {}

        for wallet in wallets:
            self.wallets[wallet.address] = wallet

        self.transactions = set(transactions)

        for transaction in transactions:

            sender = transaction.sender
            recipient = transaction.recipient

            # if wallet is in wallets, update it and reassign to wallets set
            # if wallet is not in wallets, use sender or receiver, and assign to wallets set
            self.wallets[sender.address] = \
                self.wallets.get(sender.address, sender).process_transaction(transaction)
            self.wallets[recipient.address] = \
                self.wallets.get(recipient.address, recipient).process_transaction(transaction)


    def component_containing(self, wallet: Wallet, depth: int = 5) -> Graph:
        visited_wallets = set()
        subgraph_transactions = set()
        wallets_to_visit = queue.Queue()
        wallets_to_visit.put(wallet)

        neighbors = queue.Queue()

        while (depth != 0):

            while not wallets_to_visit.empty():

                wallet = wallets_to_visit.get()

                visited_wallets.add(wallet)  # never add wallet to wallets_to_visit again

                for neighbor in wallet.transactions:

                    if neighbor.sender not in visited_wallets:
                        neighbors.put(neighbor.sender)
                        visited_wallets.add(neighbor.sender)

                    if neighbor.recipient not in visited_wallets:
                        neighbors.put(neighbor.recipient)
                        visited_wallets.add(neighbor.recipient)

                    subgraph_transactions.add(neighbor)

            depth -= 1
            wallets_to_visit = neighbors
            neighbors = queue.Queue()

        return Graph(visited_wallets, subgraph_transactions)
