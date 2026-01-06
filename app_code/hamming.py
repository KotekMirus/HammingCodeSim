def hamming_encode(data_bits: list[int]) -> list[int]:
    """Koduje dane (listę zer i jedynek reprezentujących bity) przy użyciu kodu Hamminga.
    Funkcja oblicza liczbę bitów parzystości, rozmieszcza je na odpowiednich pozycjach
    (potęgi dwójki), a następnie wylicza ich wartości tak, aby umożliwić wykrywanie
    i korekcję pojedynczego błędu bitowego.

    Args:
        data_bits (list[int]): Dane w postaci listy zer i jedynek reprezentujących bity.

    Returns:
        list[int]: Lista bitów zawierająca dane wraz z bitami parzystości.
    """
    m: int = len(data_bits)
    r: int = 0
    while (2**r) < (m + r + 1):
        r += 1
    parity_positions: list[int] = [2**i - 1 for i in range(r)]
    code_length: int = m + r
    code: list[int] = [0] * code_length
    j: int = 0
    for i in range(code_length):
        if i not in parity_positions:
            code[i] = data_bits[j]
            j += 1
    for p in parity_positions:
        number_of_ones: int = 0
        for x in range(p, code_length, (p + 1) * 2):
            for y in range(p + 1):
                if x + y > code_length - 1:
                    break
                if code[x + y] == 1:
                    number_of_ones += 1
        if number_of_ones % 2 == 1:
            code[p] = 1
    return code


def hamming_find_parity_bits_positions(code: list[int]) -> list[int]:
    """Wyznacza pozycje bitów parzystości w przekazanym kodzie Hamminga. Na podstawie
    długości zakodowanej wiadomości obliczana jest liczba bitów parzystości oraz ich
    pozycje.

    Args:
        code (list[int]): Dane zakodowane z użyciem kodu Hamminga.

    Returns:
        list[int]: Lista indeksów bitów parzystości.
    """
    code_length: int = len(code)
    parity_bits_count: int = 0
    for r in range(code_length):
        m: int = code_length - r
        if 2**r >= m + r + 1:
            parity_bits_count = r
    parity_positions: list[int] = [2**i - 1 for i in range(parity_bits_count)]
    return parity_positions


def hamming_remove_parity_bits(code: list[int]) -> list[int]:
    """Usuwa bity parzystości z zakodowanej wiadomości.

    Args:
        code (list[int]): Dane zakodowane z użyciem kodu Hamminga.

    Returns:
        list[int]: Lista bitów danych bez bitów parzystości.
    """
    parity_positions: list[int] = hamming_find_parity_bits_positions(code)
    data_bits: list[int] = [d for i, d in enumerate(code) if i not in parity_positions]
    return data_bits


def hamming_detect_and_fix(code: list[int]) -> list[int]:
    """Wykrywa i koryguje pojedynczy błąd w kodzie Hamminga. Funkcja sprawdza bity
    parzystości w celu wykrycia błędu. Jeśli zostanie wykryty błąd, jego pozycja jest
    obliczana na podstawie bitów parzystości, które wykazały jego obecność i zostaje
    on odwrócony.

    Args:
        code (list[int]): Dane zakodowane z użyciem kodu Hamminga.

    Returns:
        list[int]: Poprawiona lista bitów. Jeśli błąd nie został wykryty, są to te same
        dane, które wprowadzono na wejściu.
    """
    code_length: int = len(code)
    parity_positions: list[int] = hamming_find_parity_bits_positions(code)
    error_detection_positions: list[int] = []
    for p in parity_positions:
        number_of_ones: int = 0
        for x in range(p, code_length, (p + 1) * 2):
            for y in range(p + 1):
                if x + y > code_length - 1:
                    break
                if code[x + y] == 1:
                    number_of_ones += 1
        if number_of_ones % 2 == 1:
            error_detection_positions.append(p)
    if error_detection_positions:
        error_position: int = (
            sum(error_detection_positions) + len(error_detection_positions) - 1
        )
        code[error_position] = 0 if code[error_position] == 1 else 1
    return code
