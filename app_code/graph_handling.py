from collections import deque


def load_graph(filename: str) -> dict[str, list[str]]:
    """Wczytuje opis połączeń serwerów z pliku tekstowego i tworzy słownik reprezentujący
    graf. Plik powinien zawierać opisy połączeń w formacie:
    'ID serwera - ID serwera sąsiada,ID serwera sąsiada'

    Args:
        filename (str): Ścieżka do pliku zawierającego opis grafu.

    Returns:
        dict[str, list[str]]: Słownik reprezentujący graf, gdzie kluczem jest identyfikator
        serwera, a wartością lista identyfikatorów jego sąsiadów.
    """
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
    """Znajduje najkrótszą ścieżkę pomiędzy dwoma serwerami w grafie.

    Args:
        graph (dict[str, list[str]]): Słownik reprezentujący graf, gdzie kluczem jest
        identyfikator serwera, a wartością lista identyfikatorów jego sąsiadów.
        start (str): Identyfikator serwera początkowego.
        goal (str): Identyfikator serwera docelowego.

    Returns:
        list[str]: Lista identyfikatorów serwerów tworzących ścieżkę od start do goal
        (łącznie z nimi) lub None, jeśli ścieżka nie istnieje.
    """
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
