import threading
import queue
import time
import random
from typing import Any
from hamming import hamming_detect_and_fix
from graph_handling import find_path


class Server(threading.Thread):
    def __init__(
        self,
        server_id: str,
        servers: dict[int, Any],
        graph: dict[str, list[str]],
        sim_done: threading.Event,
    ):
        super().__init__()
        self.server_id: str = server_id
        self.servers: dict[str, Server] = servers
        self.graph: dict[str, list[str]] = graph
        self.inbox: queue.Queue = queue.Queue()
        self.running: bool = True
        self.lock = threading.Lock()
        self.previous_hop: str = None
        self.current_message: list[int] = None
        self.final_message: list[int] = None
        self.server_crashed: bool = False
        self.sim_done: threading.Event = sim_done

    def send_data(self, path: list[str], data: list[int]) -> None:
        if not path:
            return
        next_hop: str = path[0]
        with self.lock:
            self.current_message = data.copy()
        print(
            f"[Server {self.server_id}] Sending to {next_hop}: {self.current_message}"
        )
        delay: int = random.randint(6, 9)
        time.sleep(delay)
        with self.lock:
            final_message: list[int] = self.current_message.copy()
            self.current_message = None
        if self.server_crashed:
            new_path = find_path(self.graph, self.previous_hop, path[-1])
            if new_path is None:
                print(
                    f"[Server {self.server_id}] Failed to find a new path. Transmission failed."
                )
                self.sim_done.set()
            else:
                self.servers[self.previous_hop].send_data(new_path[1:], final_message)
            return
        self.servers[next_hop].inbox.put((self.server_id, final_message, path[1:]))

    def bitflip(self, number_of_bits: int) -> None:
        with self.lock:
            if self.current_message is None:
                print(
                    f"[Server {self.server_id}] Not currently sending - cannot flip bit."
                )
                return
            message_length: int = len(self.current_message)
            if number_of_bits > message_length:
                number_of_bits = message_length
            bit_positions: list[int] = random.sample(
                range(message_length), number_of_bits
            )
            for position in bit_positions:
                self.current_message[position] = (
                    0 if self.current_message[position] == 1 else 1
                )
            print(
                f"[Server {self.server_id}] Flipped bits at positions {bit_positions}. New message: {self.current_message}"
            )

    def trigger_malfunction(self):
        with self.lock:
            if self.current_message is None:
                print(
                    f"[Server {self.server_id}] Not currently sending - cannot crash."
                )
                return
            new_graph: dict[str, list[str]] = {
                k: [x for x in v if x != self.server_id]
                for k, v in self.graph.items()
                if k != self.server_id
            }
            self.graph.clear()
            self.graph.update(new_graph)
            self.server_crashed = True
            print(f"[Server {self.server_id}] Server crashed.")

    def get_final_message(self) -> list[str]:
        return self.final_message

    def run(self):
        while self.running:
            try:
                sender_id, data, remaining_path = self.inbox.get(timeout=0.5)
                with self.lock:
                    original_data: list[int] = data.copy()
                    with open("tmp/message_log.txt", "a") as file:
                        file.write(
                            f"{sender_id} {self.server_id} {"".join([str(bit) for bit in data])}\n"
                        )
                self.previous_hop = sender_id
                print(f"[Server {self.server_id}] Received from {sender_id}: {data}")
                data: list[int] = hamming_detect_and_fix(data)
                if original_data != data:
                    print(
                        f"[Server {self.server_id}] Error in data detected and fixed. Fixed data {data}"
                    )
                if remaining_path:
                    self.send_data(remaining_path, data)
                else:
                    with self.lock:
                        self.final_message = data.copy()
                    print(
                        f"[Server {self.server_id}] Final destination reached with data: {data}"
                    )
                    self.sim_done.set()
            except queue.Empty:
                continue

    def stop(self):
        self.running = False
