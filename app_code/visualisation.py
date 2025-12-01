import networkx as nx
import matplotlib.pyplot as plt
from typing import Any


def load_message_routes(filename: str) -> list[list[str]]:
    message_log: str = ""
    with open(filename, "r") as file:
        message_log = file.read()
    message_routes: list[list[str]] = []
    for line in message_log.splitlines()[1:-1]:
        message_routes.append(line.split())
    return message_routes


def create_graph_image(
    graph_dict: dict[str, list[str]], messages_routes: list[list[str]]
) -> None:
    graph: nx.Graph = nx.Graph()
    colors: list[str] = []
    for node in graph_dict.keys():
        graph.add_node(node)
        if node == messages_routes[0][0]:
            colors.append("plum")
        elif node == messages_routes[-1][1]:
            colors.append("lightgreen")
        else:
            colors.append("lightblue")
    label_dict: dict[tuple[str, str], str] = {
        (route[0], route[1]): route[2] for route in messages_routes
    }
    for main_node, connected_nodes in graph_dict.items():
        for node in connected_nodes:
            if (main_node, node) in label_dict.keys():
                graph.add_edge(
                    main_node, node, label=label_dict.get((main_node, node))[:8]
                )
            else:
                graph.add_edge(main_node, node)
    positions: dict[Any] = nx.spring_layout(graph)
    nx.draw(graph, positions, with_labels=True, node_color=colors)
    edge_labels: dict[tuple, Any] = nx.get_edge_attributes(graph, "label")
    nx.draw_networkx_edge_labels(graph, positions, edge_labels=edge_labels)
    plt.savefig("tmp/graph.png", format="PNG", dpi=300)
    plt.close()
