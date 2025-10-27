def hamming_encode(data_bits: list[int]) -> list[int]:
    code: list[int] = [0] * 22
    parity_positions: list[int] = [1, 2, 4, 8, 16]
    j: int = 0
    for i in range(1, 22):
        if i not in parity_positions:
            code[i] = data_bits[j]
            j += 1
    for p in parity_positions:
        parity: int = 0
        for i in range(1, 22):
            if i & p and i != p:
                parity ^= code[i]
        code[p] = parity
    return code[1:]
