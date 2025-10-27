import threading
import queue
import time
from typing import Any


class Server(threading.Thread):
    def __init__(self, server_id: str, servers: dict[int, Any]):
        super().__init__()
        self.server_id: str = server_id
        self.servers: dict[str, Server] = servers
        self.inbox: queue.Queue = queue.Queue()
        self.running: bool = True

    def send_data(self, path: list[str], data: list[int]) -> None:
        if not path:
            return
        next_hop: str = path[0]
        print(f"[Server {self.server_id}] Sending to {next_hop}: {data}")
        self.servers[next_hop].inbox.put((self.server_id, data, path[1:]))

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
