import server
from typing import Any
from pathlib import Path
from graph_handling import load_graph, find_path
from hamming import hamming_encode, hamming_remove_parity_bits
import threading
import copy
import os


def start_servers(
    servers_number: int, graph: dict[str, list[str]], sim_done: threading.Event
) -> dict[str, server.Server]:
    """Tworzy i uruchamia wątki serwerów.

    Args:
        servers_number (int): Liczba serwerów do utworzenia.
        graph (dict[str, list[str]]): Słownik zawierający wszystkie połączenia między
        serwerami (ID serwera - lista ID serwerów bezpośrednio podłączonych do tego serwera).
        sim_done (threading.Event): Zdarzenie informujące o zakończeniu symulacji.

    Returns:
        dict[str, server.Server]: Słownik zawierający wszystkie pary ID - obiekt serwera.
    """
    servers: dict[str, server.Server] = {}
    for i in range(1, servers_number + 1):
        s = server.Server(str(i), servers, graph, sim_done)
        servers[str(i)] = s
        s.start()
    return servers


def gather_sim_info(sim_done: threading.Event) -> list[Any]:
    """Zbiera od użytkownika wszystkie dane potrzebne do uruchomienia symulacji.
    Konwertuje wiadomość podaną przez użytkownika na listę intów (0, 1), wywołuje
    inicjalizację serwerów oraz wywołuje funkcję znajdującą ścieżkę między serwerami
    podanymi przez użytkownika. Ponadto przygotowuje foldery wykorzystywane przez program.

    Args:
        sim_done (threading.Event): Zdarzenie sygnalizujące zakończenie symulacji.

    Returns:
        list[Any]: Lista zawierająca wiadomość w postaci listy zer i jedynek, słownik ze
        wszystkimi parami ID - obiekt serwera, ścieżkę przesyłu wiadomości, kopię grafu
        połączeń potrzebną do wizualizacji.
    """
    tmp_folder_path: Path = Path("tmp")
    tmp_folder_path.mkdir(exist_ok=True)
    final_folder_path: Path = Path("final")
    final_folder_path.mkdir(exist_ok=True)
    if Path("tmp/message_log.txt").is_file():
        os.remove("tmp/message_log.txt")
    print("\nStart of gathering simulation info.\n")
    message_type: str = input("Enter message type (B - binary, P - plaintext): ")
    if message_type.upper() == "B":
        while True:
            input_message: str = input("Enter message like 01101001...: ").strip()
            if set(input_message) <= {"0", "1"}:
                break
    else:
        input_message: str = input("Enter message like Hello Janek...: ")
        input_message = "".join(format(ord(c), "08b") for c in input_message)
    message: list[int] = [int(bit) for bit in input_message]
    while True:
        graph_file_path: str = input("Enter graph file path: ")
        if Path(graph_file_path).is_file():
            break
    graph: dict[str, list[str]] = load_graph(graph_file_path)
    graph_copy: dict[str, list[str]] = copy.deepcopy(graph)
    servers: dict[str, server.Server] = start_servers(
        max(map(int, graph.keys())), graph, sim_done
    )
    while True:
        starting_point: str = input("Enter starting server: ").strip()
        ending_point: str = input("Enter ending server: ").strip()
        if starting_point in servers and ending_point in servers:
            break
    path: list[str] = find_path(graph, starting_point, ending_point)
    return [message, servers, path, graph_copy]


def command_listener(
    servers: dict[str, server.Server], sim_done: threading.Event
) -> None:
    """Nasłuchuje poleceń użytkownika w trakcie trwania symulacji. Funkcja działa w osobnym
    wątku. W każdej iteracji sprawdza czy użytkownik wpisał w konsoli komendę zaczynającą
    się na bitflip, crash lub stop. Odpowiadają one kolejno wywołaniom wprowadzenia błędu
    w wiadomości, zasymulowaniu awarii serwera i zakończeniu symulacji.

    Args:
        servers (dict[str, server.Server]): Słownik zawierający wszystkie pary ID -
        obiekt serwera.
        sim_done (threading.Event): Zdarzenie informujące o zakończeniu symulacji.
    """
    while True:
        user_input: str = input().strip().lower()
        if user_input.startswith("bitflip"):
            args: list[str] = user_input.split()
            server_id: str = "0"
            number_of_bits: int = 1
            if len(args) == 2:
                server_id = args[1]
            elif len(args) == 3:
                server_id = args[1]
                number_of_bits = int(args[2])
            if server_id in servers:
                servers[server_id].bitflip(number_of_bits)
        elif user_input.startswith("crash"):
            args: list[str] = user_input.split()
            server_id: str = "0"
            if len(args) == 2:
                server_id = args[1]
            if server_id in servers:
                servers[server_id].trigger_malfunction()
        elif user_input == "stop":
            sim_done.set()
            end_sim(servers)
            break


def end_sim(servers: dict[str, server.Server]) -> None:
    """Zatrzymuje wszystkie serwery i kończy działanie symulacji.

    Args:
        servers (dict[str, server.Server]): Słownik zawierający wszystkie pary ID -
        obiekt serwera.
    """
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
    """Uruchamia właściwą symulację przesyłania wiadomości. Rozpoczyna od zapisania
    wiadomości do pliku. Następnie wywołuje funkcję, która koduje wiadomość za pomocą
    kodu Hamminga. Dalej zakodowana wiadomość zostaje wysłana z serwera startowego.
    Kiedy transfer wiadomości się zakończy (dotrze do serwera docelowego lub symulacja
    zostanie przerwana), ostateczna wiadomość jest pobierana z serwera docelowego.
    Z pomocą odpowiedniej funkcji zostają z niej usunięte bity parzystości i zostaje
    zapisana do pliku (zapisane zostają również identyfikatory serwerów startowego
    i końcowego).

    Args:
        message (list[int]): Wiadomość do przesłania w postaci listy zer i jedynek.
        servers (dict[str, server.Server]): Słownik zawierający wszystkie pary ID -
        obiekt serwera.
        path (list[str]): Lista identyfikatorów serwerów stanowiąca trasę wiadomości.
        sim_done (threading.Event): Zdarzenie informujące o zakończeniu symulacji.
    """
    with open("tmp/message_log.txt", "a") as file:
        file.write("".join([str(bit) for bit in message]) + "\n")
    destination_server: str = path[-1]
    print("\nMessage: ", message, "\n", sep="")
    encoded_message: list[int] = hamming_encode(message)
    print("Encoded message:", encoded_message)
    print("\nStart of the simulation.\n")
    servers[path[0]].send_data(path[1:], encoded_message)
    sim_done.wait()
    final_message: list[int] = servers[destination_server].get_final_message()
    if final_message is not None:
        final_message: list[int] = hamming_remove_parity_bits(final_message)
    end_sim(servers)
    print("Original message:", message)
    print("Final message:", final_message)
    print("Message transfer success:", message == final_message)
    with open("tmp/message_log.txt", "a") as file:
        if final_message is not None:
            file.write("".join([str(bit) for bit in final_message]))
        else:
            file.write("None")
        file.write(f"\n{path[0]} {path[-1]}")
