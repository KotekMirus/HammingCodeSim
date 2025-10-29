from collections import deque


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
