import pytest
from app_code.graph_handling import load_graph, find_path


def test_load_graph(tmp_path):
    graph_file = tmp_path / "graph.txt"
    graph_file.write_text(
        """
        1 - 3,6
        2 - 3,4,6
        3 - 1,2,4,5
        4 - 2,3
        5 - 3
        6 - 1,2
        """
    )
    graph: dict[str, list[str]] = {
        "1": ["3", "6"],
        "2": ["3", "4", "6"],
        "3": ["1", "2", "4", "5"],
        "4": ["2", "3"],
        "5": ["3"],
        "6": ["1", "2"],
    }
    loaded_graph: dict[str, list[str]] = load_graph(graph_file)
    assert loaded_graph == graph


def test_find_path_1():
    graph: dict[str, list[str]] = {
        "1": ["2", "3", "4"],
        "2": ["1", "3", "5"],
        "3": ["1", "2"],
        "4": ["1", "6"],
        "5": ["2", "8"],
        "6": ["4", "9"],
        "7": ["8", "10"],
        "8": ["5", "7", "9"],
        "9": ["6", "8"],
        "10": ["7"],
    }
    path: list[str] = find_path(graph, "2", "7")
    assert path == ["2", "5", "8", "7"]


def test_find_path_2():
    graph: dict[str, list[str]] = {
        "1": ["2", "3", "4"],
        "2": ["1", "3", "5"],
        "3": ["1", "2"],
        "4": ["1", "6"],
        "5": ["2"],
        "6": ["4"],
        "7": ["8", "10"],
        "8": ["7", "9"],
        "9": ["8"],
        "10": ["7"],
    }
    path: list[str] = find_path(graph, "2", "7")
    assert path is None
