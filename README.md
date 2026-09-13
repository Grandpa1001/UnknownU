# UNKNOWN

Obserwatorium sztucznego życia. Jedyna sprawczość to **START** — potem tylko się patrzy.

Świat 4000×4000 toczy się sam: organizmy jedzą, uczą się, szukają partnerów i wymierają. Front niczym nie steruje; backend nie ma endpointów kontroli.

## Jak to działa

Organizmy mają genom (cechy, krótki program, rozmiar) i energię.

- **Energia** to sygnał głodu, nie licznik „im więcej, tym rodź”. Gdy zapas jest w porządku, można chodzić, myśleć i szukać kogoś. Gdy zaczyna spadać od ostatniego szczytu, konieczne staje się szukanie jedzenia.
- **Jedzenie:** jabłka na drzewach (więcej energii) i jagody na krzakach (mniej, ale odrastają). Głodny zjada; najedzony nie obozuje przy drzewie.
- **Rozród** wymaga pary: dwoje spokojnych energetycznie osobników w zasięgu. Dziecko dziedziczy mix obu genomów, czasem z mutacją.
- **Uczenie** w czasie życia: ocena akcji (ruch, jedzenie, rozród…) zostaje przy osobniku, nie przechodzi na potomstwo.
- **Fizyka:** kolizje i odbicia, pęd, słup na środku mapy i wiatr wirowy wokół niego. Mapa jest torusem — krawędź łączy się z przeciwległą.

Bieg kończy wymarcie albo limit ticków. Zostaje kronika: przyczyna, pokolenia, dziennik.

## Wymagania

- Python 3.12+
- Node.js 18+
- Make (opcjonalnie; komendy da się powtórzyć ręcznie)

## Uruchomienie

```bash
make install
```

Dwa terminale:

```bash
make backend    # http://127.0.0.1:8000
make frontend   # http://127.0.0.1:5173
```

Otwórz [http://127.0.0.1:5173](http://127.0.0.1:5173), ustaw nazwę / liczbę organizmów / seed i wciśnij START.

Na mapie: przeciąganie przesuwa widok, kółko myszy przybliża. Klik w organizm otwiera kartotekę (tylko odczyt). Tagowanie i śledzenie są lokalne — serwer o nich nie wie.

Stan świata zapisuje się w `data/unknown.db` (katalog jest w `.gitignore`). Restart backendu wznawia ten sam tick, o ile baza istnieje.

## Testy

```bash
make test
```

## Symulacja bez UI

Headless runner w `backend`:

```bash
make sim          # 10 ticków, seed 1
make sim-life     # dłuższy bieg ze zdarzeniami
make sim-extinct  # świat bez jedzenia
make sim-evo      # więcej organizmów, mutacje
make sim-learn    # podgląd pamięci org_1
make sim-save     # zapis do data/unknown.db
make sim-resume   # dokręcenie zapisanego świata
```

Pełne flagi: `python -m app.simulation.runner --help` (katalog `backend`, venv aktywny).

## API

Jedyna mutacja to utworzenie świata. Reszta to odczyt.

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| `POST` | `/api/worlds` | Nowy świat (`name`, `organism_count` 1–20, opcjonalnie `seed`, `max_tick`) |
| `GET` | `/api/worlds/{id}` | Snapshot (teren, drzewa, krzaki, organizmy…) |
| `GET` | `/api/worlds/{id}/stats` | Populacja, pokolenie, jabłka, jagody |
| `GET` | `/api/worlds/{id}/events` | Ostatnie zdarzenia |
| `GET` | `/api/worlds/{id}/chronicle` | Kronika po końcu biegu |
| `GET` | `/api/organisms/{id}` | Kartoteka, także po śmierci |
| `WS` | `/ws/worlds/{id}` | Stan na żywo (~10 ticków/s) |
| `GET` | `/health` | `{ "ok": true }` |

## Układ repozytorium

```
backend/     FastAPI, silnik ticków, genom, fizyka, SQLite
frontend/    React + Vite + Pixi — mapa i obserwatorium
data/        lokalna baza (nie w gicie)
```

Tick trwa 0,1 s. Front łączy się z `http://127.0.0.1:8000` (`VITE_API_BASE` / `VITE_WS_BASE`, gdy trzeba inaczej).

## Licencja

[MIT](LICENSE)
