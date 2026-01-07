import pytest
from app_code.hamming import (
    hamming_encode,
    hamming_find_parity_bits_positions,
    hamming_remove_parity_bits,
    hamming_detect_and_fix,
)


def test_hamming_encode_1():
    data: list[int] = [1, 0, 0, 1]
    encoded_data: list[int] = hamming_encode(data)
    assert encoded_data == [0, 0, 1, 1, 0, 0, 1]


def test_hamming_encode_2():
    data: list[int] = [1, 1, 0, 1, 1]
    encoded_data: list[int] = hamming_encode(data)
    assert encoded_data == [0, 0, 1, 0, 1, 0, 1, 1, 1]


def test_hamming_find_parity_bits_positions_1():
    encoded_data: list[int] = [0, 0, 1, 1, 0, 0, 1]
    parity_positions: list[int] = hamming_find_parity_bits_positions(encoded_data)
    assert parity_positions[:3] == [0, 1, 3]


def test_hamming_find_parity_bits_positions_2():
    encoded_data: list[int] = [0, 0, 1, 0, 1, 0, 1, 1, 1]
    parity_positions: list[int] = hamming_find_parity_bits_positions(encoded_data)
    assert parity_positions[:4] == [0, 1, 3, 7]


def test_hamming_remove_parity_bits_1():
    encoded_data: list[int] = [0, 0, 1, 1, 0, 0, 1]
    data: list[int] = hamming_remove_parity_bits(encoded_data)
    assert data == [1, 0, 0, 1]


def test_hamming_remove_parity_bits_2():
    encoded_data: list[int] = [0, 0, 1, 0, 1, 0, 1, 1, 1]
    data: list[int] = hamming_remove_parity_bits(encoded_data)
    assert data == [1, 1, 0, 1, 1]


def test_hamming_detect_and_fix_1():
    # no error in encoded data
    encoded_data: list[int] = [0, 0, 1, 0, 1, 0, 1, 1, 1]
    fixed_data: list[int] = hamming_detect_and_fix(encoded_data)
    assert encoded_data == fixed_data


def test_hamming_detect_and_fix_2():
    # one error in encoded data (data bit)
    encoded_data_with_one_error: list[int] = [0, 0, 0, 0, 1, 0, 1, 1, 1]
    fixed_data: list[int] = hamming_detect_and_fix(encoded_data_with_one_error)
    assert fixed_data == [0, 0, 1, 0, 1, 0, 1, 1, 1]


def test_hamming_detect_and_fix_3():
    # one error in encoded data (parity bit)
    encoded_data_with_one_error: list[int] = [0, 0, 1, 1, 1, 0, 1, 1, 1]
    fixed_data: list[int] = hamming_detect_and_fix(encoded_data_with_one_error)
    assert fixed_data == [0, 0, 1, 0, 1, 0, 1, 1, 1]
