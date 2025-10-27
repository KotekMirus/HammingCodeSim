import server
from collections import deque
from typing import Any
import threading


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


def start_servers(
    servers_number: int, sim_done: threading.Event
) -> dict[str, server.Server]:
    servers: dict[str, server.Server] = {}
    for i in range(1, servers_number + 1):
        s = server.Server(str(i), servers, sim_done)
        servers[str(i)] = s
        s.start()
    return servers


def gather_sim_info(sim_done: threading.Event) -> list[Any]:
    print("\nStart of gathering simulation info.\n")
    input_message: str = input("Enter message like 01101001...: ").strip()
    message: list[int] = [int(bit) for bit in input_message]
    graph_file_path: str = input("Enter graph file path: ")
    starting_point: str = input("Enter starting server: ").strip()
    ending_point: str = input("Enter ending server: ").strip()
    graph: dict[str, list[str]] = load_graph(graph_file_path)
    path: list[str] = find_path(graph, starting_point, ending_point)
    servers: dict[int, server.Server] = start_servers(
        max(map(int, graph.keys())), sim_done
    )
    return [message, servers, path]


def command_listener(servers, sim_done: threading.Event):
    while True:
        user_input: str = input().strip().lower()
        if user_input.startswith("bitflip"):
            args: list[str] = user_input.split()
            server_id: str = args[1]
            if server_id in servers:
                servers[server_id].bitflip()
        elif user_input == "stop":
            sim_done.set()
            end_sim(servers)
            break


def end_sim(servers: dict[str, server.Server]) -> None:
    for s in servers.values():
        s.stop()
    for s in servers.values():
        s.join()
    print("\nAll servers stopped. End of simulation.\n")


def run_sim(
    message: list[int],
    servers: dict[str, server.Server],
    path: list[str],
    sim_done: threading.Event,
) -> None:
    print("\nStart of the simulation.\n")
    servers[path[0]].send_data(path[1:], message)
    sim_done.wait()
    end_sim(servers)


def main() -> None:
    sim_done: threading.Event = threading.Event()
    sim_info: list[Any] = gather_sim_info(sim_done)
    threading.Thread(
        target=command_listener, args=(sim_info[1], sim_done), daemon=True
    ).start()
    run_sim(sim_info[0], sim_info[1], sim_info[2], sim_done)


if __name__ == "__main__":
    main()
