import server
from typing import Any
from pathlib import Path
from graph_handling import load_graph, find_path
from hamming import hamming_encode, hamming_remove_parity_bits
import threading


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
    while True:
        input_message: str = input("Enter message like 01101001...: ").strip()
        if set(input_message) <= {"0", "1"}:
            break
    message: list[int] = [int(bit) for bit in input_message]
    while True:
        graph_file_path: str = input("Enter graph file path: ")
        if Path(graph_file_path).is_file():
            break
    graph: dict[str, list[str]] = load_graph(graph_file_path)
    servers: dict[str, server.Server] = start_servers(
        max(map(int, graph.keys())), sim_done
    )
    while True:
        starting_point: str = input("Enter starting server: ").strip()
        ending_point: str = input("Enter ending server: ").strip()
        if starting_point in servers and ending_point in servers:
            break
    path: list[str] = find_path(graph, starting_point, ending_point)
    return [message, servers, path]


def command_listener(servers, sim_done: threading.Event):
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
    destination_server: str = path[-1]
    print("\nMessage: ", message, "\n", sep="")
    encoded_message = hamming_encode(message)
    print("Encoded message:", encoded_message)
    print("\nStart of the simulation.\n")
    servers[path[0]].send_data(path[1:], encoded_message)
    sim_done.wait()
    final_message: list[int] = servers[destination_server].get_final_message()
    final_message: list[int] = hamming_remove_parity_bits(final_message)
    end_sim(servers)
    print("Original message:", message)
    print("Final message:", final_message)
    print("Message transfer success:", message == final_message)
