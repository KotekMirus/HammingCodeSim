import threading
import queue
import time
import random
from typing import Any


class Server(threading.Thread):
    def __init__(self, server_id: str, servers: dict[int, Any]):
        super().__init__()
        self.server_id: str = server_id
        self.servers: dict[str, Server] = servers
        self.inbox: queue.Queue = queue.Queue()
        self.running: bool = True
        self.lock = threading.Lock()
        self.current_message: list[int] = None

    def send_data(self, path: list[str], data: list[int]) -> None:
        if not path:
            return
        next_hop: str = path[0]
        with self.lock:
            self.current_message = data.copy()
        print(
            f"[Server {self.server_id}] Sending to {next_hop}: {self.current_message}"
        )
        delay = random.randint(6, 9)
        time.sleep(delay)
        with self.lock:
            final_message = self.current_message.copy()
            self.current_message = None
        self.servers[next_hop].inbox.put((self.server_id, final_message, path[1:]))

    def bitflip(self) -> None:
        with self.lock:
            if self.current_message is None:
                print(
                    f"[Server {self.server_id}] not currently sending - cannot flip bit."
                )
                return
            bit_position = random.randint(0, len(self.current_message) - 1)
            self.current_message[bit_position] = (
                0 if self.current_message[bit_position] == 1 else 1
            )
            print(
                f"[Server {self.server_id}] Bit flipped at position {bit_position}. New message: {self.current_message}"
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
            except queue.Empty:
                continue

    def stop(self):
        self.running = False
