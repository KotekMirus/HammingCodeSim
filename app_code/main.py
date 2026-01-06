from typing import Any
from simulation_handling import gather_sim_info, run_sim, command_listener
from visualisation import load_message_routes, create_graph_gif
import threading


def main() -> None:
    """Uruchamia wszystkie fazy symulacji. Wywołuje funkcję pobierającą dane symulacji
    od użytkownika, tworzy wątek nasłuchujący poleceń użytkownika oraz rozpoczyna
    właściwą symulację przesyłania wiadomości pomiędzy serwerami. Na koniec wywołuje
    funkcję generującą GIF przedstawiający przebieg symulacji.
    """
    sim_done: threading.Event = threading.Event()
    sim_info: list[Any] = gather_sim_info(sim_done)
    threading.Thread(
        target=command_listener, args=(sim_info[1], sim_done), daemon=True
    ).start()
    run_sim(sim_info[0], sim_info[1], sim_info[2], sim_done)
    create_graph_gif(sim_info[3], *load_message_routes("tmp/message_log.txt"))


if __name__ == "__main__":
    main()
