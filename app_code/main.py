import server
from collections import deque
from typing import Any


def load_graph(filename: str) -> dict[str, list[str]]:
    graph: dict[str, list[str]] = {}
    with open(filename, "r") as file:
        for line in file:
            if "-" not in line:
                continue
            server, neighbors = line.strip().split("-")
            server = server.strip()
            neighbors = [n.strip() for n in neighbors.split(",")]
            graph[server] = neighbors
    return graph


def find_path(graph: dict[str, list[str]], start: str, goal: str) -> list[str]:
    if start not in graph or goal not in graph:
        return None
    queue = deque([(start, [start])])
    visited = set()
    while queue:
        (current, path) = queue.popleft()
        if current == goal:
            return path
        visited.add(current)
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))
    return None


def start_servers(servers_number: int) -> dict[str, server.Server]:
    servers: dict[int, server.Server] = {}
    for i in range(1, servers_number + 1):
        s = server.Server(str(i), servers)
        servers[str(i)] = s
        s.start()
    return servers


def gather_sim_info() -> list[Any]:
    print("\nStart of gathering simulation info.\n")
    input_message: str = input("Enter message like 01101001...: ").strip()
    message: list[int] = [int(bit) for bit in input_message]
    graph_file_path: str = input("Enter graph file path: ")
    starting_point: str = input("Enter starting server: ").strip()
    ending_point: str = input("Enter ending server: ").strip()
    graph: dict[str, list[str]] = load_graph(graph_file_path)
    path: list[str] = find_path(graph, starting_point, ending_point)
    servers: dict[int, server.Server] = start_servers(max(map(int, graph.keys())))
    return [message, servers, path]


def end_sim(servers: dict[str, server.Server]) -> None:
    for s in servers.values():
        s.stop()
    for s in servers.values():
        s.join()
    print("\nAll servers stopped. End of simulation.\n")


def run_sim(
    message: list[int], servers: dict[str, server.Server], path: list[str]
) -> None:
    print("\nStart of the simulation.\n")
    servers[path[0]].send_data(path[1:], message)


def main() -> None:
    sim_info: list[Any] = gather_sim_info()
    run_sim(sim_info[0], sim_info[1], sim_info[2])


if __name__ == "__main__":
    main()
