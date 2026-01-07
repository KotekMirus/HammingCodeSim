# Symulacja transmisji danych - Kod Hamminga

## Opis

Projekt umożliwia symulację przesyłania wiadomości pomiędzy serwerami połączonymi w graf. Wiadomość wprowadzona przez użytkownika zostaje zakodowana z wykorzystaniem kodu Hamminga. W trakcie transmisji użytkownik może wydawać komendy symulujące różne problemy, takie jak przeskok bitu (bitflip) czy awaria serwera. Każdy serwer sprawdza poprawność wiadomości natychmiast po jej odebraniu i potrafi skorygować maksymalnie jeden błąd bitowy. W przypadku awarii serwera automatycznie wyznaczana jest nowa najkrótsza ścieżka do serwera docelowego. Po zakończeniu symulacji generowane są plik PNG przedstawiający pełną trasę wiadomości oraz plik GIF prezentujący trasę w formie animacji.

## Struktura projektu

/app_code -> pliki Pythona z kodem aplikacji

/resources -> czcionka

/tests -> testy jednostkowe

## Jak uruchomić?

Windows

```
python app_code/main.py
```

macOS

```
python3 app_code/main.py
```

## Jak to działa?

Po uruchomieniu aplikacji użytkownik zostanie poproszony o podanie danych symulacji:

- wiadomości do przesłania,
- identyfikatora serwera nadawcy,
- identyfikatora serwera odbiorcy,
- ścieżki do pliku tekstowego zawierającego opis połączeń w grafie.

Plik tekstowy z opisem grafu powinien mieć następujący format:

```
ID_serwera - ID_serwera_sąsiada,ID_serwera_sąsiada
ID_serwera - ID_serwera_sąsiada
ID_serwera - ID_serwera_sąsiada,ID_serwera sąsiada,ID_serwera_sąsiada
...
```

Po wprowadzeniu wszystkich danych aplikacja wyznacza najkrótszą trasę przesyłu wiadomości i uruchamia serwery jako osobne wątki. Każdy serwer zatrzymuje się na losowy czas od 6 do 9 sekund przed przekazaniem wiadomości dalej. W tym czasie użytkownik może wprowadzić jedną z następujących komend:

```
bitflip id_serwera opcjonalna_ilość_bitów
```

```
crash id_serwera
```

Kiedy wiadomość dotrze do serwera docelowego (lub transmisja zostanie przerwana ręcznie albo z powodu braku dostępnej ścieżki), aplikacja wygeneruje plik PNG przedstawiający pełną trasę wiadomości oraz plik GIF prezentujący trasę w formie animacji. Użytkownik może je znaleźć w folderze final.