import server
from typing import Any


def gather_sim_info() -> list[Any]:
    print("\nStart of gathering simulation info.\n")
    input_message: str = input("Enter message like 01101001...: ").strip()
    message: list[int] = [int(bit) for bit in input_message]
    servers_number: int = int(input("Enter number of servers: ").strip())
    servers: dict[int, server.Server] = {}
    for i in range(1, servers_number + 1):
        s = server.Server(i, servers)
        servers[i] = s
        s.start()
    print(
        "Enter paths like '1->3->4' (each in new line). When you enter 'start' simulation will begin."
    )
    paths: list[list[int]] = []
    while True:
        user_input: str = input("Path: ").strip()
        if user_input.lower() == "start":
            break
        path: list[int] = None
        try:
            path = [int(server_num.strip()) for server_num in user_input.split("->")]
        except:
            print("Invalid format. Use 'X->Y->Z'.")
            continue
        paths.append(path)
    return [message, servers, paths]


def end_sim(servers: dict[int, server.Server]) -> None:
    for s in servers.values():
        s.stop()
    for s in servers.values():
        s.join()
    print("\nAll servers stopped. End of simulation.\n")


def run_sim(
    message: list[int], servers: dict[int, server.Server], paths: list[list[int]]
) -> None:
    print("\nStart of the simulation.\n")
    for path in paths:
        start_point: int = path[0]
        if start_point not in servers:
            print(f"Server {start_point} does not exist.")
            continue
        servers[start_point].send_data(path[1:], message)


def main():
    sim_info: list[Any] = gather_sim_info()
    run_sim(sim_info[0], sim_info[1], sim_info[2])


if __name__ == "__main__":
    main()
