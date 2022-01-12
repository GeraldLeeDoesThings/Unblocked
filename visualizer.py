import networkx as nx
import matplotlib.pyplot as plt
import json


class Graph:

    def __init__(self):
        self.edges = []

    def add_edge(self, fr, to, weight):
        self.edges.append([fr, to, weight])

    def visualize(self):
        g = nx.DiGraph()
        for fr, to, weight in self.edges[:10]:
            g.add_edge(fr, to, weight=weight)
        nx.draw_networkx(g)
        plt.show()


g = Graph()

with open("data.json", "r") as file:
    data = json.load(file)
    for _, block in data.items():
        for transaction in json.loads(block)['transactions']:
            g.add_edge(
                transaction['from'],
                transaction['to'],
                float(transaction['value'])/(10**18)
            )

g.visualize()
