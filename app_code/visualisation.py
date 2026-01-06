import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont, ImageFile
from typing import Any
import os


def load_message_routes(filename: str) -> tuple[list[list[str]], str, str, str, str]:
    """Wczytuje z pliku trasy i stany przesyłania wiadomości. Funkcja wyodrębnia kolejne
    etapy przesyłania wiadomości pomiędzy serwerami, a także informacje o wiadomości
    początkowej, końcowej oraz serwerach nadawcy i odbiorcy.

    Args:
        filename (str): Ścieżka do pliksu zawierającego trasę jaką przebyła wiadomość
        oraz startową i końcową wersję wiadomości.

    Returns:
        tuple[list[list[str]], str, str, str, str]: Krotka zawierająca kolejno listę tras
        przesyłania wiadomości, wiadomość początkową, wiadomość końcową, identyfikator
        serwera początkowego, identyfikator serwera końcowego.
    """
    message_log: str = ""
    with open(filename, "r") as file:
        message_log = file.read()
    message_routes: list[list[str]] = []
    message_log_lines: list[str] = message_log.splitlines()
    for line in message_log_lines[1:-2]:
        message_routes.append(line.split())
    final_nodes: list[str] = message_log_lines[-1].split()
    return (
        message_routes,
        message_log_lines[0],
        message_log_lines[-2],
        final_nodes[0],
        final_nodes[1],
    )


def create_graph_image(
    graph_dict: dict[str, list[str]],
    messages_routes: list[list[str]],
    first_node: str,
    last_node: str,
    filename: str,
) -> None:
    """Tworzy obraz PNG grafu (połączonych serwerów) z wiadomością pomiędzy serwerami,
    które brały udział w jej transferze. Funkcja rysuje graf połączeń serwerów przy
    użyciu bibliotek NetworkX oraz Matplotlib. Serwery początkowy i końcowy są wyróżnione
    kolorami fioletowym i zielonym, a na odpowiednich połączeniach węzłów dodane są
    etykiety zawierające fragmenty wiadomości.

    Args:
        graph_dict (dict[str, list[str]]): Słownik zawierający wszystkie połączenia między
        serwerami (ID serwera - lista ID serwerów bezpośrednio podłączonych do tego serwera).
        messages_routes (list[list[str]]): Lista etapów przesyłu wiadomości (każdy element
        zawiera ID nadawcy, ID odbiorcy, wiadomość).
        first_node (str): Identyfikator serwera początkowego.
        last_node (str): Identyfikator serwera końcowego.
        filename (str): Nazwa pliku wyjściowego (obrazu PNG).
    """
    graph: nx.Graph = nx.Graph()
    colors: list[str] = []
    for node in graph_dict.keys():
        graph.add_node(node)
        if node == first_node:
            colors.append("plum")
        elif node == last_node:
            colors.append("lightgreen")
        else:
            colors.append("lightblue")
    label_dict: dict[tuple[str, str], str] = {
        (route[0], route[1]): route[2] for route in messages_routes
    }
    for main_node, connected_nodes in graph_dict.items():
        for node in connected_nodes:
            if (main_node, node) in label_dict.keys():
                graph.add_edge(
                    main_node, node, label=label_dict.get((main_node, node))[:8]
                )
            else:
                graph.add_edge(main_node, node)
    positions: dict[Any] = nx.spring_layout(graph)
    nx.draw(graph, positions, with_labels=True, node_color=colors)
    edge_labels: dict[tuple, Any] = nx.get_edge_attributes(graph, "label")
    nx.draw_networkx_edge_labels(graph, positions, edge_labels=edge_labels)
    plt.savefig(filename, format="PNG", dpi=300)
    plt.close()


def cleanup_tmp() -> None:
    """Usuwa tymczasowe pliki graficzne z folderu tmp."""
    for filename in os.listdir("tmp"):
        path = os.path.join("tmp", filename)
        try:
            os.remove(path)
        except PermissionError:
            pass


def create_graph_gif(
    graph_dict: dict[str, list[str]],
    messages_routes: list[list[str]],
    start_message: str,
    final_message: str,
    first_node: str,
    last_node: str,
) -> None:
    """Generuje animację GIF przedstawiającą transfer wiadomości w sieci serwerów. Na
    początku funkcji w pętli wywoływana jest funkcja generująca obrazy PNG odpowiadające
    kolejnym etapom transferu wiadomości. Dalej generowane są obrazy PNG zawierające
    wiadomość startową i finalną (pierwsza i ostatnia klatka animacji). Na koniec obrazy
    te są łączone w animację GIF. Dodatkowo funkcja wywołuje generowanie pliku PNG
    przedstawiającego całkowitą trasę wiadomości.

    Args:
        graph_dict (dict[str, list[str]]): Słownik zawierający wszystkie połączenia między
        serwerami (ID serwera - lista ID serwerów bezpośrednio podłączonych do tego serwera).
        messages_routes (list[list[str]]): Lista etapów przesyłu wiadomości (każdy element
        zawiera ID nadawcy, ID odbiorcy, wiadomość).
        start_message (str): Wiadomość początkowa (przed kodowaniem).
        final_message (str): Wiadomość końcowa (po dekodowaniu).
        first_node (str): Identyfikator serwera początkowego.
        last_node (str): Identyfikator serwera końcowego.
    """
    cleanup_tmp()
    image_count: int = len(messages_routes)
    for i in range(image_count):
        create_graph_image(
            graph_dict,
            messages_routes[: i + 1],
            first_node,
            last_node,
            f"tmp/{i+1}.png",
        )
    create_graph_image(
        graph_dict, messages_routes, first_node, last_node, f"final/final_route.png"
    )
    image_example: ImageFile = Image.open("tmp/1.png")
    width, height = image_example.size
    font: Any = ImageFont.truetype("resources/Roboto-Medium.ttf", int(height * 0.15))
    image_with_start_message: Image = Image.new("RGB", (width, height), (255, 255, 255))
    draw: ImageDraw = ImageDraw.Draw(image_with_start_message)
    draw.text(
        (0.05 * width, 0.45 * height),
        start_message,
        fill=(0, 0, 0),
        font=font,
    )
    image_with_start_message.save("tmp/0.png")
    image_with_final_message: Image = Image.new("RGB", (width, height), (255, 255, 255))
    draw: ImageDraw = ImageDraw.Draw(image_with_final_message)
    draw.text(
        (0.05 * width, 0.45 * height),
        final_message,
        fill=(0, 0, 0),
        font=font,
    )
    image_with_final_message.save(f"tmp/{image_count+1}.png")
    all_frames: list[str] = [f"tmp/{i}.png" for i in range(image_count + 2)]
    gif_frames: list[Any] = [Image.open(png) for png in all_frames]
    gif_frames[0].save(
        "final/message_transfer.gif",
        save_all=True,
        append_images=gif_frames[1:],
        duration=1000,
        loop=0,
    )
    for frame in gif_frames:
        frame.close()
