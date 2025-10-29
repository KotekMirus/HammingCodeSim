import threading
import queue
import time
import random
from typing import Any


class Server(threading.Thread):
    def __init__(
        self, server_id: str, servers: dict[int, Any], sim_done: threading.Event
    ):
        super().__init__()
        self.server_id: str = server_id
        self.servers: dict[str, Server] = servers
        self.inbox: queue.Queue = queue.Queue()
        self.running: bool = True
        self.lock = threading.Lock()
        self.current_message: list[int] = None
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

    def run(self):
        while self.running:
            try:
                sender_id, data, remaining_path = self.inbox.get(timeout=0.5)
                print(f"[Server {self.server_id}] Received from {sender_id}: {data}")
                if remaining_path:
                    self.send_data(remaining_path, data)
                else:
                    print(
                        f"[Server {self.server_id}] Final destination reached with data: {data}"
                    )
                    self.sim_done.set()
            except queue.Empty:
                continue

    def stop(self):
        self.running = False
