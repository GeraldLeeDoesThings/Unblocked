from __future__ import annotations
import matplotlib.pyplot as plt
import networkx as nx
import queue
from typing import *
from utils import Tree


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

    def add_wallet(self, wallet: Wallet):
        self.wallets[wallet.address] = wallet

    def add_transaction(self, transaction: Transaction):
        self.transactions.add(transaction)

    def find_component(self, wallet: Wallet, depth: int = 5) -> Graph:
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

    def visualize(self):
        g = nx.DiGraph()
        for t in self.transactions:
            g.add_edge(t.sender.address, t.recipient.address, weight=t.amount)
        nx.draw_networkx(g)
        plt.show()

    def make_tree(self, source_wallet: Wallet, from_block_num: int, to_block_num: int) -> Tree[Wallet]:

        if from_block_num > to_block_num:
            return Tree(source_wallet, [])

        filtered_transactions = []
        min_closest_block_num = to_block_num
        for transaction in source_wallet.get_transactions_out():
            if transaction.block == min_closest_block_num:
                filtered_transactions.append(transaction)
            elif from_block_num <= transaction.block < min_closest_block_num:
                min_closest_block_num = transaction.block
                filtered_transactions = [transaction]

        return Tree(
            source_wallet,
            [self.make_tree(transaction.recipient, min_closest_block_num + 1, to_block_num)
             for transaction in filtered_transactions]
        )


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
        return hash(self.address)


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
