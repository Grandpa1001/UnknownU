# UNKNOWN — Plan developmentu (MVP lokalne)

**Data**: 2026-09-11  
**Źródła**: `Analiza.MD` (decyzje), `UNKNOWN_MVP_PLAN.md`, `Podsumowanie.md`  
**Cel tego pliku**: doprowadzić do **działającego MVP na własnej maszynie** — świat żyje sam, UI jest do wglądu  
**Poza zakresem tego planu**: Hostinger, nginx, SSL, 7 dni na VPS

---

## 0. Co znaczy „MVP działa lokalnie”

Otwierasz dwa procesy (backend + frontend), w przeglądarce tworzysz świat, patrzysz jak organizmy same jedzą / rozmnażają się / umierają. Nie ma przycisku, który zmienia świat. Zamykasz serwer, odpalasz znowu — ten sam tick, te same osobniki.

```
localhost:5173  →  obserwatorium (React + Pixi)
localhost:8000  →  FastAPI + silnik (Python) + SQLite
```

**Nie czekamy na deploy**, żeby zobaczyć efekt. Każdy kamień milowy kończy się dwiema rzeczami:

1. **Sprawdzenie efektu** — czy ten kawałek w ogóle działa (komenda / ekran).
2. **Kontrola kursu** — czy to nadal ten sam produkt z `Analiza.MD` i czy realnie zbliża nas do działającej aplikacji na localhost.

Efekt bez kursu = działa, ale może nas wyprowadzić w bok (god-mode, VPS, pixel-art bez silnika). Kurs bez efektu = ładna teoria, brak aplikacji. Oba muszą przejść, zanim ruszamy następny kamień.

---

## 1. Zasady pracy

1. **Jeden kamień = jeden widoczny efekt.** Nie merge’ujemy „infrastruktury bez dowodu”.
2. **Test headless przed UI.** Silnik musi dawać wynik w terminalu, zanim powstanie viewport.
3. **Tick w testach jest natychmiastowy.** `world.tick()` nie śpi. Sleep 100 ms jest tylko w pętli live.
4. **UI nie woła mutacji świata.** Po `POST /api/worlds` tylko `GET` + WebSocket.
5. **Najpierw kółka, potem sprite’y.** Oglądalność > trailer pixel-art.
6. **Nie ruszamy Hostingera** w tym dokumencie.
7. **Po każdym kamieniu: efekt + kurs.** Nie zaczynamy M(n+1), jeśli kontrola kursu ma choć jedno STOP.

---

## 1a. Kompas — do czego to ma dojść

To jest docelowa aplikacja. Każdy kamień musi dać się wskazać palcem na tej liście. Jeśli kawałek kodu nie zasila żadnego punktu — jest zbędny albo za wczesny.

| # | Cel końcowy (localhost) | Które kamienie to budują |
|---|-------------------------|--------------------------|
| 1 | Świat sam tyka | M1, M2 |
| 2 | Organizmy jedzą, umierają, rozmnażają się, mutują, uczą się | M3, M4, M5 |
| 3 | Restart procesu nie kasuje historii | M6 |
| 4 | Da się to zobaczyć w przeglądarce na żywo | M7, M8 |
| 5 | Jedyna sprawczość: START; dalej UI do wglądu | M9, M10, M11 |
| 6 | Wygląda jak mały świat, nie jak log | M8, M12 |
| 7 | Bieg umie się skończyć (wymarcie / tick-cap) | M6, M11 |
| 8 | `make dev` → działa u nas, bez VPS | M0, M12 |

Pięć zdań, które **nie mogą paść** w żadnym kamieniu (dryf = STOP):

1. „Dodajmy przycisk, żeby im pomóc / przetestować.”
2. „Najpierw ładne sprite’y, silnik potem.”
3. „Na razie bez persistencji, jakoś to będzie.”
4. „UI może na chwilę sterować organizmem.”
5. „To MVP lokalne, ale od razu Docker i Hostinger.”

Szablon kontroli kursu (powtarza się po każdym M):

```
Kontrola kursu
├─ Zgodnie z planem?     (czy zrobiliśmy TYLKO to, co kamień każe)
├─ Prowadzi do celu?     (który punkt 1–8 z kompasu właśnie odblokowaliśmy)
├─ Nic nie zepsuliśmy?   (czy wcześniejsze PASS-y nadal działają)
└─ STOP / idziemy dalej
```

Stałe z analizy (punkt startu balansu):

| Stała | Wartość |
|-------|---------|
| Mapa | 4000×4000, torus |
| Tick live | 10 Hz (100 ms) |
| MVP live-cap (lokalnie) | np. 50_000 ticków albo wymarcie — nie trzeba czekać 7 dni |
| Organizmy start | 3 (formularz 1–20) |
| Energia start | 400–600 |
| Jabłko | +150, max 3–5 / drzewo, respawn 200 ticków |
| Drzewa | 30–40 |
| Kwiaty | 50–100, tylko dekoracja |
| MOVE / TURN / SENSE / WAIT / THINK / egzystencja | 5 / 1 / 2 / 0.5 / 1 / 0.2 |
| REPRODUCE | −200, dziecko 100 energii |
| Mutacja | 30%, jedna zmiana |
| Hitbox organizmu | 8–12 px; sprite później 24×32 |

Dla testów lokalnych: mniejszy świat **tylko jeśli** 4000×4000 boli przy debugowaniu terenu. Domyślnie zostawiamy 4000×4000; w testach jednostkowych wolno `width=400, height=400`.

---

## 2. Stack lokalny

| Warstwa | Wybór |
|---------|--------|
| Silnik + API | Python 3.11, FastAPI, Uvicorn |
| Baza | SQLite, WAL, plik `data/unknown.db` |
| Frontend | React + Vite + Pixi.js |
| Dev | `make dev` albo dwa terminale |
| Testy silnika | `pytest` |
| Docker | opcjonalnie na końcu; **nie blokuje** kamieni A–C |

---

## 3. Docelowa struktura repo

```
UnknownU/
├─ Analiza.MD
├─ DEV.md                 ← ten plik
├─ Makefile
├─ backend/
│  ├─ pyproject.toml      (albo requirements.txt)
│  ├─ tests/
│  └─ app/
│     ├─ main.py          FastAPI + start pętli
│     ├─ api/
│     │  ├─ routes.py     POST worlds, GET *
│     │  └─ ws.py         push stanu
│     ├─ persistence/
│     │  ├─ db.py
│     │  └─ snapshot.py
│     └─ simulation/
│        ├─ world.py
│        ├─ organism.py
│        ├─ genome.py
│        ├─ actions.py
│        ├─ environment.py  drzewa, jabłka, kwiaty, fertility
│        ├─ terrain.py
│        └─ runner.py       pętla 10 Hz
├─ frontend/
│  ├─ package.json
│  └─ src/
│     ├─ App.jsx
│     ├─ pages/Start.jsx, Observatory.jsx
│     ├─ components/Viewport, Inspector, Stats, EventLog
│     └─ hooks/useWorldSocket.js, useCamera.js
└─ data/                  gitignored, SQLite
```

---

## 4. Mapa kamieni

```
WARSTWA A — silnik w terminalu
  M0  szkielet
  M1  świat tyka, teren, drzewa, spawn
  M2  ruch + sense
  M3  energia, jabłka, śmierć
  M4  reprodukcja + mutacja
  M5  uczenie
  M6  SQLite + snapshot + wymarcie

WARSTWA B — wgląd w przeglądarce
  M7  API + WebSocket (bez UI)
  M8  viewport (kształty) + kamera
  M9  START + obserwatorium (stats + log)

WARSTWA C — da się wrócić i oglądać
  M10 inspector (klik = wgląd)
  M11 tag / follow + ekran końca
  M12 sprite’y lite + test lokalny end-to-end
```

Nie zaczynamy M(n+1), dopóki **Sprawdzenie efektu** i **Kontrola kursu** z M(n) nie przechodzą.

Po całej warstwie (A / B / C) jest **bramka warstwy**: szersze pytanie „czy w ogóle zmierzamy do działającej aplikacji, czy tylko zbieramy moduły”.

```
M0 → M1 → M2 → M3 → M4 → M5 → M6 → [BRAMKA A]
                                      ↓
                         M7 → M8 → M9 → [BRAMKA B]
                                      ↓
                    M10 → M11 → M12 → [BRAMKA C = aplikacja działa]
```

Szacunek: A ~ kilka wieczorów, B ~ kilka, C ~ kilka. Nie kotwiczymy dat — kotwiczymy efekt + kurs.

---

## WARSTWA A — świat żyje bez UI

### M0 — Szkielet repo

**Cel.** Dwa puste serwisy wstają lokalnie. Testy idą.

**Budujemy.**

- `backend/` z FastAPI hello `GET /health` → `{ "ok": true }`
- `frontend/` Vite + React hello „UNKNOWN”
- `Makefile`: `make backend`, `make frontend`, `make test`
- `.gitignore`: `data/`, `node_modules/`, `.venv/`, `__pycache__/`
- `pytest` z jednym testem `test_health` albo `test_placeholder`

**Nie budujemy:** Docker, silnika, Pixi.

**Sprawdzenie efektu.**

```bash
# terminal 1
cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000
# curl
curl -s http://127.0.0.1:8000/health
# oczekiwane: {"ok":true}

# terminal 2
cd frontend && npm run dev
# przeglądarka: http://127.0.0.1:5173  → napis UNKNOWN

make test
# oczekiwane: pytest PASS
```

**PASS gdy:** health odpowiada, frontend się ładuje, testy zielone.

**Kontrola kursu — czy idziemy do działającej aplikacji?**

| Pytanie | TAK = idziemy | STOP = zbaczamy |
|---------|---------------|-----------------|
| Czy to lokalny szkielet, nie VPS/Docker? | dwa porty na localhost | compose, nginx, Hostinger |
| Czy frontend jest pustą ramką, nie grą? | napis UNKNOWN, zero Pixi | canvas, sprite’y, sterowanie |
| Czy da się to potem złożyć w `make dev`? | Makefile / dwa polecenia | „jakoś odpalimy ręcznie folderami bez kontraktu” |
| Kompas | odblokowany punkt **8** (zalążek) | nic z punktów 1–7 jeszcze nie udajemy że działa |

**Regresja:** brak (pierwszy kamień).  
**Idziemy do M1 tylko gdy:** curl + przeglądarka + pytest przechodzą i nie ma deploya.

---

### M1 — Świat, teren, drzewa, organizmy (jeszcze martwe)

**Cel.** Da się stworzyć `World` w Pythonie i wypisać, co jest na mapie. Tick zwiększa licznik. Organizmy stoją.

**Budujemy.**

- `World(seed, width, height, initial_organisms)`
- `terrain.py` — Perlin (albo prosty value-noise), 4 typy kafelków 16×16 w logice siatki
- 30–40 drzew z 3–5 jabłkami
- 50–100 kwiatów
- N organizmów w losowych pozycjach, energia 400–600, genom bazowy
- `world.tick()` na razie: `current_tick += 1` + wiek += 1
- CLI: `python -m app.simulation.runner --ticks 10 --seed 1`

**Sprawdzenie efektu.**

```bash
cd backend
python -m app.simulation.runner --ticks 10 --seed 1 --print
```

Oczekiwany stdout (sens, nie dokładny format):

```
seed=1 tick=10 organisms=3 trees=37 apples=112 flowers=81
org_1 pos=(1234, 890) energy=512 feature=antena
org_2 ...
terrain[0][0]=grass
```

```bash
pytest tests/test_world_init.py
# ten sam seed → te same pozycje drzew
# tick=10 po pętli
# 0 < organisms <= N
```

**PASS gdy:** dwa uruchomienia z `--seed 1` dają ten sam teren i te same startowe pozycje drzew. Organizmy istnieją. Tick rośnie.

**Widać efekt:** w terminalu jest świat, nie pusty serwer.

**Kontrola kursu — czy idziemy do działającej aplikacji?**

| Pytanie | TAK | STOP |
|---------|-----|------|
| Czy świat istnieje niezależnie od UI? | `runner` w terminalu | „najpierw narysujemy mapę w Pixi” |
| Czy to jabłka na drzewach, nie luźne rośliny? | trees + apples w dumpie | plants[] jako jedzenie |
| Czy seed jest powtarzalny (potem START + inny seed w UI)? | dwa runy = ten sam teren | los bez seeda |
| Czy organizm ma pola, które inspector później pokaże? | id, pos, energy, feature, genome | goły `(x,y)` bez genomu |
| Kompas | zalążek punktu **1** | udajemy że aplikacja już „żyje” (jeszcze nie — stoją) |

**Regresja:** `make test` i `/health` z M0 nadal działają.  
**Idziemy do M2 tylko gdy:** dump pokazuje drzewa/jabłka/organizmy i M0 nie padł.

---

### M2 — Ruch i percepcja

**Cel.** Organizmy się ruszają i „widzą” jabłka. Energia jeszcze może być uproszczona (koszt MOVE już schodzić).

**Budujemy.**

- Akcje: `MOVE`, `TURN`, `WAIT`, `SENSE`
- Torus: wyjście za krawędź → druga strona
- `SENSE`: w promieniu ~100 px lista jabłek / organizmów (kierunek, dystans)
- Program bazowy zaczyna od SENSE → jeśli jedzenie w pobliżu, skręć / idź
- Koszty MOVE/TURN/WAIT/SENSE z tabeli; jeszcze bez śmierci jeśli wolisz odłożyć do M3 — **lepiej już odejmować energię**, śmierć w M3

**Sprawdzenie efektu.**

```bash
python -m app.simulation.runner --ticks 100 --seed 1 --print-every 20
```

Pozycje **nie** są identyczne z tickiem 0. Przynajmniej jeden organizm zmienił `x` lub `y`.

```bash
pytest tests/test_movement.py
# torus wrap: x=3999 + krok → mały x
# sense przy jabłku zwraca food z dystansem < promienia
# MOVE obniża energię o 5
```

**PASS gdy:** dump pokazuje dryf pozycji; test torusa i sense zielone.

**Widać efekt:** „chodzą”, nie stoją.

**Kontrola kursu — czy idziemy do działającej aplikacji?**

| Pytanie | TAK | STOP |
|---------|-----|------|
| Czy chodzą **sami** (program), nie od klawiszy? | brak inputu w runnerze | WASD, click-to-move, nawet „tymczasowo” |
| Czy torus jest w silniku (viewport później tylko pokaże)? | wrap w teście | ściany / spadanie poza mapę |
| Czy SENSE zwraca jabłka — pod przyszłe EAT i rysowanie? | food w percepcji | sense „na oko” bez danych |
| Kompas | punkt **1** prawie pełny (świat tyka i się rusza) | fizyka colliders, pathfinding AAA |

**Regresja:** `runner --ticks 10 --seed 1` z M1 nadal wstaje.  
**Idziemy do M3 tylko gdy:** pozycje dryfują i nikt nie steruje z klawiatury.

---

### M3 — Jabłka, energia, śmierć

**Cel.** Jedzenie działa. Głód zabija. Jabłka wracają na drzewa. Śmierć zostawia fertility buff (odchody mogą być markerem w stanie, bez sprite’a).

**Budujemy.**

- `EAT`: w zasięgu drzewa z jabłkiem → +150, jabłko znika
- Egzystencja −0.2 / tick
- `energy <= 0` → organizm martwy, event `death`, boost jabłek w okolicy na 500 ticków
- Respawn jabłka co 200 ticków na losowym drzewie (nie ponad max 5)

**Sprawdzenie efektu.**

```bash
python -m app.simulation.runner --ticks 2000 --seed 1 --print-every 200
```

W logu pojawiają się linie w stylu:

```
tick=340 EAT org_1 apple_12 energy 480→630
tick=910 DEATH org_3 energy=0 age=910
tick=200 apples=... (liczba się zmienia)
```

```bash
pytest tests/test_eating.py tests/test_death.py
# stój na jabłku → eat → +150, jabłko usunięte
# energy=0 → usunięty z żywych
# po 200 tickach liczba jabłek może wrócić w górę
```

Szybki test „czy umierają z głodu bez jedzenia”:

```bash
python -m app.simulation.runner --ticks 5000 --seed 1 --no-apples
# oczekiwane: status=extinct, living=0
```

**PASS gdy:** widać EAT i/lub DEATH w logu; bez jabłek świat wymiera; pytest zielony.

**Widać efekt:** świat ma konsekwencje, nie tylko spacer.

**Kontrola kursu — czy idziemy do działającej aplikacji?**

| Pytanie | TAK | STOP |
|---------|-----|------|
| Czy śmierć i jedzenie są w **silniku**, nie w UI? | eventy w logu runnera | „kliknij żeby zjeść / ożywić” |
| Czy bez jabłek świat kończy się sam (potem overlay M11)? | `extinct` | pętla wieczna z martwymi ciałami albo auto-spawn gracza |
| Czy EAT jest przy drzewie, nie „roślina na ziemi”? | zasięg drzewa | nowy byt food-tile jako główne jedzenie |
| Kompas | punkt **2** (jeść/umierać) + zalążek **7** | cheat `energy=9999` zostawiony w API |

**Regresja:** ruch z M2 nadal działa; seed 1 nadal odpala świat.  
**Idziemy do M4 tylko gdy:** widać EAT lub DEATH i `--no-apples` kończy bieg.

---

### M4 — Reprodukcja i mutacja

**Cel.** Przy wysokiej energii powstaje dziecko. Genom kopiuje się. Czasem widać inną cechę / trait.

**Budujemy.**

- `REPRODUCE` gdy energia ≥ próg (trait) i ≥ 200 kosztu
- Dziecko obok rodzica, energia 100, `parent_id`, `generation+1`
- 30% szans: jedna mutacja (trait ±0.1 | slot programu | size ±1 | feature)
- Eventy `birth`, `mutation`

**Sprawdzenie efektu.**

```bash
python -m app.simulation.runner --ticks 8000 --seed 42 --organisms 5 --print-events
```

Oczekiwane w eventach:

```
BIRTH child=org_6 parent=org_2 generation=2
MUTATION org_6 trait.bravery 0.50→0.60
```

```bash
pytest tests/test_reproduction.py
# parent energy 500 → po reproduce ~300, living+1
# 100% kopii genomu gdy wymusimy mutation_rate=0
# mutation_rate=1 → różnica w 1 polu
```

**PASS gdy:** `living` bywa > N start; jest `parent_id`; pytest na mutację zielony.

**Widać efekt:** genealogia, nie stała trójka.

**Kontrola kursu — czy idziemy do działającej aplikacji?**

| Pytanie | TAK | STOP |
|---------|-----|------|
| Czy dzieci powstają z energii rodzica, nie z przycisku? | REPRODUCE w programie | `POST /breed`, slider „dodaj osobnika” w trakcie biegu |
| Czy mutacja jest 1 zmiana / 30%, czytelna w evencie? | event MUTATION | chromosomy, 2 rodziców, losowy nowy gatunek |
| Czy `parent_id` + generation są w stanie (inspector M10)? | pola na organizmie | dziecko bez genealogii |
| Kompas | punkt **2** (rozmnażanie + mutacja) | hodowla sterowana przez gracza |

**Regresja:** EAT/DEATH z M3 nadal w logu; pytest M1–M3 zielone.  
**Idziemy do M5 tylko gdy:** living bywa > start i da się wskazać rodzica.

---

### M5 — Uczenie w trakcie życia

**Cel.** Udana akcja (dodatnia delta energii) zwiększa `predictionScore`; kolejna decyzja to uwzględnia. THINK trwa kilka ticków, podnosi jakość, kręciołek później w UI.

**Budujemy.**

- Pamięć: `last_action`, `energy_delta`, `predictionScore`
- Wybór akcji = program + traits + learned scores + `stupidity`
- `THINK`: organizm stoi, płaci 1/tick, potem lepsza decyzja

**Sprawdzenie efektu.**

```bash
pytest tests/test_learning.py -s
```

Scenariusz: podłożyć „MOVE zawsze daje +20” przez N ticków → `predictionScore["MOVE"]` rośnie.  
Scenariusz: MOVE zawsze −15 → score spada.

```bash
python -m app.simulation.runner --ticks 3000 --seed 7 --print-memory org_1
```

Oczekiwane: niezerowe `predictionScore`, nie same zera.

**PASS gdy:** test uczenia nie zależy od Pixi; score się rusza.

**Widać efekt:** w dumpie pamięci widać faworyzowanie akcji, nie tylko genom.

**Kontrola kursu — czy idziemy do działającej aplikacji?**

| Pytanie | TAK | STOP |
|---------|-----|------|
| Czy to proste `predictionScore`, nie sieć neuronowa / LLM? | słownik akcja→score | PyTorch, prompt, „agent” |
| Czy nauka ginie ze śmiercią osobnika (nie gatunku)? | pamięć na organizmie | globalny brain |
| Czy THINK zostawia stan do kręciołka w UI później? | flaga `isThinking` | think niewidoczne w stanie |
| Kompas | punkt **2** domknięty (jeść/umierać/rodzić/uczyć) | „learning nie potrzebne, skip” — wtedy cel z Analizy dziurawy |

**Regresja:** reprodukcja z M4 nadal działa.  
**Idziemy do M6 tylko gdy:** score się rusza w teście i nie ma ML-frameworka.

---

### M6 — Persistencja, statusy, snapshot

**Cel.** Świat przeżywa restart procesu. Wymarcie zatrzymuje pętlę. Koniec tick-cap zatrzymuje pętlę.

**Budujemy.**

- Tabele: `worlds`, `organisms`, `events`, `snapshots`
- Snapshot co N ticków (lokalnie np. co 100 albo 3600)
- `World.save` / `World.load`
- Status: `running | extinct | finished`
- `runner` zapisuje przed exit

**Sprawdzenie efektu.**

```bash
python -m app.simulation.runner --ticks 500 --seed 1 --db data/unknown.db
# zapamiętaj tick i liczbę żywych

python -m app.simulation.runner --resume --db data/unknown.db --ticks 10
# start od zapisanego ticka, nie od 0
```

```bash
sqlite3 data/unknown.db "SELECT current_tick, status FROM worlds;"
sqlite3 data/unknown.db "SELECT type, COUNT(*) FROM events GROUP BY type;"
```

```bash
pytest tests/test_persistence.py
# save → load: ten sam tick, te same id, te same pozycje
```

Wymarcie:

```bash
python -m app.simulation.runner --no-apples --ticks 99999 --db data/extinct.db
sqlite3 data/extinct.db "SELECT status FROM worlds;"
# extinct
```

**PASS gdy:** resume nie resetuje świata; eventy są w SQL; wymarcie ustawia status, proces nie crashuje.

**Widać efekt:** zamykasz terminal, odpalasz znowu, historia trwa.

**Kontrola kursu — czy idziemy do działającej aplikacji?**

| Pytanie | TAK | STOP |
|---------|-----|------|
| Czy resume to ten sam świat, nie nowy seed? | tick ≥ zapisanego | zawsze `World()` od zera |
| Czy status `running/extinct/finished` jest w DB (UI M11 to pokaże)? | kolumna status | tylko print w terminalu |
| Czy SQLite lokalne, nie Postgres „bo produkcja”? | `data/unknown.db` | nowy serwis bazy |
| Kompas | punkt **3** i **7** (silnik) | „zapiszemy jak będzie frontend” |

**Regresja:** `make test` (M1–M5) + `runner --ticks 100` bez DB nadal działa.  
**Idziemy do M7 tylko gdy:** kill+resume zachowuje tick **oraz** przejdzie bramka warstwy A.

---

### Bramka warstwy A — czy silnik w ogóle złoży się w aplikację?

Zatrzymaj się. Nie otwieraj Pixi, dopóki to nie jest prawda:

- [ ] `python -m app.simulation.runner --ticks 1000 --seed 1 --print-events` kończy się bez crasha
- [ ] W logu są przynajmniej dwa z: `EAT`, `DEATH`, `BIRTH`, `MUTATION` (albo świadomy powód balansu, nie brak kodu)
- [ ] `--resume` kontynuuje ten sam tick
- [ ] Żadnego sterowania z stdin / klawiatury
- [ ] Dane które UI będzie malować już istnieją: pozycje, drzewa, jabłka, genomy, eventy, status
- [ ] Kompas 1, 2, 3, 7 (część silnikowa) = TAK; 4–6, 8 jeszcze nie — i **nie udajemy że tak**

**Jeśli bramka A pada:** wróć do kamienia, który kłamie. Frontend na martwym albo nieserializowalnym świecie **nie** przybliża nas do celu.

**Warstwa A zamknięta** = lokalny symulator bez okna, gotowy do podłączenia pod API. Nie „pół silnika + już rysujemy”.

---

## WARSTWA B — da się patrzeć, nie da się dotknąć

### M7 — HTTP + WebSocket

**Cel.** Przeglądarka / curl widzi żywy stan. Tworzenie świata to jedyny POST.

**Budujemy.**

- `POST /api/worlds` `{ name, organism_count, seed, max_tick }` → start `runner` w tle
- `GET /api/worlds/{id}` snapshot do rysowania (teren meta, drzewa, jabłka, organizmy)
- `GET /api/worlds/{id}/stats`
- `GET /api/worlds/{id}/events?limit=50`
- `GET /api/organisms/{id}`
- `WS /ws/worlds/{id}` — serwer push: pozycje, jabłka, eventy, tick (~10 Hz)
- Brak endpointów feed/move/kill

Silnik z M6 podpięty do aplikacji: jeden świat naraz na MVP lokalne jest OK (`active_world_id`).

**Sprawdzenie efektu.**

```bash
uvicorn app.main:app --reload --port 8000

curl -s -X POST http://127.0.0.1:8000/api/worlds \
  -H 'Content-Type: application/json' \
  -d '{"name":"lokalny","organism_count":3,"seed":1}'
# → {"id":1,...}

curl -s http://127.0.0.1:8000/api/worlds/1 | python -m json.tool
# tick > 0 po chwili
# organisms[].position się zmienia przy drugim GET

# brak sterowania:
curl -s -o /dev/null -w "%{http_code}" \
  -X POST http://127.0.0.1:8000/api/organisms/org_1/feed
# 404 lub 405
```

WebSocket (wstępnie):

```bash
npx --yes wscat -c ws://127.0.0.1:8000/ws/worlds/1
# co ~100ms JSON z tick i positions
```

**PASS gdy:** dwa GET-y w odstępie sekundy pokazują inny tick / pozycje; feed nie istnieje; WS leci sam.

**Widać efekt:** żywy backend bez frontendu.

**Kontrola kursu — czy idziemy do działającej aplikacji?**

| Pytanie | TAK | STOP |
|---------|-----|------|
| Czy jedyny POST to stworzenie świata? | `POST /api/worlds` + same GET/WS | feed, move, kill, pause, breed |
| Czy WS **pcha** stan, klient nic nie rozkazuje? | serwer → klient | klient wysyła akcje na WS |
| Czy payload ma to, co Pixi namaluje w M8? | tick, organisms, trees, apples, events | goły tick bez pozycji |
| Czy to nadal jeden lokalny proces + SQLite? | uvicorn :8000 | Redis, kolejki, mikroserwisy |
| Kompas | punkt **4** (zalążek: widać live bez okna) | „dodajmy panel admina do sterowania testami” |

**Regresja:** `runner` headless z warstwy A nadal działa obok API (albo jest tym samym silnikiem). `pytest` A zielone.  
**Idziemy do M8 tylko gdy:** dwa GET-y pokazują ruch **i** feed zwraca 404/405.

---

### M8 — Viewport (kształty) + kamera

**Cel.** Widać mapę i poruszające się kropki. Pan/zoom. Żadnego sterowania bytami.

**Budujemy.**

- Pixi canvas
- Warstwy: kolorowe kafelki terenu (prostokąty), kółka drzew, czerwone jabłka, niebieskie organizmy
- Kamera: drag = pan, scroll = zoom
- Podłączenie WS: interpolacja opcjonalna; na MVP skok co tick jest OK
- Klik na razie może nic nie robić (inspector = M10) albo podświetlać — bez requestu mutującego

**Sprawdzenie efektu.**

1. Backend z M7 działa, świat created.
2. Frontend `/world/1` (tymczasowo wpisane ID).
3. Widzisz teren i poruszające się kropki.
4. Przeciągasz myszą — mapa jedzie. Scroll — zoom.
5. Devtools → Network: WS otwarty, zero POST-ów poza ewentualnym create.

**PASS gdy:** po 5 sekundach kropki są gdzie indziej; kamera działa; organizmów nie da się przeciągnąć.

**Widać efekt:** „to jest świat”, nie JSON.

**Kontrola kursu — czy idziemy do działającej aplikacji?**

| Pytanie | TAK | STOP |
|---------|-----|------|
| Czy to podgląd silnika, nie druga logika świata? | pozycje z WS | frontend sam rusza kropki |
| Czy kamera = wgląd, nie sterowanie? | pan/zoom | drag organizmu, click-to-walk |
| Czy kształtów wystarczy (sprite’y = M12)? | kółka/prostokąty | tydzień pixel-artu, 0 inspectora |
| Network: po wejsciu na świat zero POST-ów akcji? | tylko WS + GET | ukryty POST przy kliku |
| Kompas | punkt **4** i zalążek **6** | gra, w którą się klika żeby grać |

**Regresja:** curl z M7 nadal zwraca rosnący tick.  
**Idziemy do M9 tylko gdy:** kropki same chodzą i nie da się ich przeciągnąć.

---

### M9 — Ekran START + ramka obserwatorium

**Cel.** Jedyne miejsce sprawczości + ciągły wgląd w liczby i dziennik.

**Budujemy.**

- `/` formularz: nazwa, slider 1–20, seed auto/ręczny, `START`
- Po starcie redirect `/world/{id}`
- Panel stats: population, generation, births, deaths, apples, tick
- Event log (ostatnie ~50), zdania jak w analizie
- Żadnego pauza / speed / karm

**Sprawdzenie efektu.**

1. Wejdź na `http://127.0.0.1:5173`
2. Ustaw 3 organizmy, seed `1`, START
3. Jesteś w obserwatorium, tick rośnie, log się zapełnia
4. Odśwież stronę — ten sam świat, tick nie wraca do 0
5. Przejdź palcem po UI: nie ma przycisku akcji wobec świata

**PASS gdy:** create → oglądanie działa; refresh nie tworzy nowego świata sam z siebie; log pokazuje EAT/BIRTH/DEATH gdy się zdarzą.

**Widać efekt:** pełna pętla produktu bez inspectora.

**Kontrola kursu — czy idziemy do działającej aplikacji?**

| Pytanie | TAK | STOP |
|---------|-----|------|
| Czy START jest jedynym formularzem sprawczym? | `/` → create → `/world/id` | edycja świata w locie, drugi panel „spawn” |
| Czy stats/log tylko czytają API? | liczby z GET/WS | przycisk który zeruje liczniki w silniku |
| Czy nie ma pauzy / speed / karmienia „na chwilę”? | brak w UI i w API | speed 1x/2x, pause |
| Czy odświeżenie strony wznawia **ten sam** id? | persistencja M6 widoczna w UI | F5 = nowy świat |
| Kompas | punkt **5** (zalążek) + **8** mocniejszy | wracamy do CLI bo „UI niepotrzebne” — to nie aplikacja |

**Regresja:** viewport z M8 nadal rusza kropki; `pytest` + health.  
**Idziemy do M10 tylko gdy:** przejdzie bramka warstwy B.

---

### Bramka warstwy B — czy to już składa się w aplikację?

To pierwszy moment, gdy ktoś obcy może „uruchomić UNKNOWN” bez Pythona w głowie.

- [ ] `make dev` (albo dwa znane polecenia) → START w przeglądarce
- [ ] Po START widać teren, drzewa, poruszające się organizmy, rosnący tick
- [ ] Log/stats zmieniają się same
- [ ] F5 nie tworzy nowego świata
- [ ] W UI **nie ma** akcji wobec organizmów
- [ ] Kompas 1–4 = TAK; 5 częściowo; 6 jeszcze surowe — OK
- [ ] Warstwa A nadal przechodzi (`make test`, runner)

**Jeśli bramka B pada:** nie dokładamy inspectora ani sprite’ów. Aplikacja to pętla START → oglądanie. Bez niej M10–M12 to ozdoby.

**Warstwa B zamknięta** = da się patrzeć, nie da się dotknąć. To już jest produkt, tylko surowy.

---

## WARSTWA C — wracasz i oglądasz

### M10 — Inspector (wgląd)

**Cel.** Klik = kartoteka. Świat bez zmian.

**Budujemy.**

- Hit-test sprite/kółka
- Panel: id, age, energy, generation, parent, children, traits, program, feature
- GET `/api/organisms/{id}` (albo dane już z WS)
- Pierścień zaznaczenia
- Zamknięcie panelu nie wpływa na silnik

**Sprawdzenie efektu.**

1. Klik w niebieską kropkę → panel z genomem
2. Energia w panelu spada / rośnie zgodnie z ruchem
3. Network: tylko GET albo dane z WS, zero POST
4. Klik w trawę → odznaczenie, nic się nie spawnuje

```bash
# twardy test API
curl -s http://127.0.0.1:8000/api/organisms/org_1 | python -m json.tool
# genome.traits, program, morphology
```

**PASS gdy:** da się powiedzieć „to ten z anteną / bravery 0.6”; klik nie przesuwa organizmu.

**Widać efekt:** serial ma bohaterów, nie tylko tłum.

**Kontrola kursu — czy idziemy do działającej aplikacji?**

| Pytanie | TAK | STOP |
|---------|-----|------|
| Czy klik = kartoteka, nie rozkaz? | panel read-only | slider trait, przycisk kill, edit DNA |
| Czy dane inspectora = silnik, nie wymysł frontu? | GET/WS zgadza się z panelem | frontend „dorysowuje” genom |
| Czy zamknięcie panelu nic nie robi światu? | tylko UI state | request przy unselect |
| Kompas | punkt **5** (wgląd w osobnika) | inspector jako debug-konsola do cheatów |

**Regresja:** START + viewport + log z M9; Network bez POST po kliku.  
**Idziemy do M11 tylko gdy:** genom widać i klik nie rusza ciała.

---

### M11 — Tag, Follow, koniec biegu

**Cel.** Przywiązanie bez władzy. Świat umie się skończyć na ekranie.

**Budujemy.**

- Tag: `localStorage`, znacznik nad jednostką, lista otagowanych
- Follow: kamera lerp do celu, gubi się gdy umrze (komunikat, nie crash)
- Ekran `extinct` / `finished` (tick cap) — overlay, viewport zostaje do podglądu archiwum
- Follow/Tag nie idą do backendu jako komendy świata

**Sprawdzenie efektu.**

1. Taguj osobnika, odśwież — tag wraca z localStorage
2. Follow — kamera jedzie za nim
3. `--no-apples` albo niski `max_tick` → overlay końca, status w stats
4. Po końcu nadal działa inspector (archiwum), START nowego świata jest **nowym** id

**PASS gdy:** śmierć followowanego nie psuje canvas; koniec biegu jest czytelny; tag nie istnieje w SQLite organizmu.

**Widać efekt:** da się kibicować bez ingerencji; bieg ma ending.

**Kontrola kursu — czy idziemy do działającej aplikacji?**

| Pytanie | TAK | STOP |
|---------|-----|------|
| Czy tag/follow są u widza, nie w SQLite organizmu? | `localStorage` | kolumna `tagged` w `organisms` |
| Czy koniec biegu jest ekranem, nie crashem? | overlay extinct/finished | biała strona, pętla 100% CPU |
| Czy po końcu nadal jest **wgląd**, nie „ożywić”? | inspector działa, brak resurrect | przycisk restart tych samych osobników |
| Kompas | punkt **5** i **7** (UI) | pauza żeby zdążyć otagować = ingerencja w czas świata |

**Regresja:** inspector M10; persistencja F5.  
**Idziemy do M12 tylko gdy:** ending widać i tag nie leci do backendu jako komenda świata.

---

### M12 — Sprite’y lite + akceptacja lokalna

**Cel.** Wygląda jak mała gra do oglądania, nie jak debug draw. MVP uznane za działające lokalnie.

**Budujemy (minimum z analizy, nie Throungles full).**

- 4 kafelki terenu
- drzewo, jabłko, 2–3 kwiaty
- organizm 24×32, 4 kierunki × 2 klatki (albo nawet 1 klatka + flip)
- overlay feature (5 prostych)
- krętiolek przy THINK
- fade przy śmierci
- pierścień select

Jeśli brak artysty: **geometryczne sprite’y** (zaokrąglone ciało + kreska anteny) są legalne na PASS, byle feature było rozróżnialne.

**Sprawdzenie efektu — test akceptacyjny MVP (rób w tej kolejności).**

| # | Krok | Oczekiwany efekt |
|---|------|------------------|
| 1 | `make dev` (albo dwa terminale) | API health + UI START |
| 2 | START, 3 organizmy, seed 1 | viewport, ruch, drzewa, jabłka |
| 3 | Czekaj aż ktoś zje albo umrze | event w logu + zmiana stats |
| 4 | Klik organizm | inspector z genomem |
| 5 | Tag + Follow | kamera i znacznik; zero POST świata |
| 6 | Szukaj w UI przycisku karmienia / pauzy | nie ma |
| 7 | Zabij backend, wstań, odśwież UI | ten sam id, tick ≥ poprzedni |
| 8 | Nowy świat innym seedem | inny teren / inne startowe drzewa |
| 9 | Świat bez jabłek albo krótki max_tick | overlay extinct/finished |
| 10 | `pytest` w backendzie | all green |

**PASS całego MVP lokalnego:** wszystkie 10 kroków.  
To jest definicja „działa”. Nie: „mamy 80% kodu”.

**Kontrola kursu — ostatnia przed „gotowe”**

| Pytanie | TAK | STOP |
|---------|-----|------|
| Czy sprite’y tylko malują stan silnika? | feature overlay z genomu | animacja która kłamie (je, choć energy nie wstaje) |
| Czy nie odłożyliśmy checklisty „bo ładnie wygląda”? | 10/10 z tabeli wyżej | „sztuka done, persistencja jutro” |
| Czy nadal zero sprawczości po START? | przejście palcem po UI | nowy przycisk „wkradł się” przy polishu |
| Czy to localhost, nie nagle VPS? | `make dev` | deploy w tym kamieniu |
| Kompas | punkty **1–8 wszystkie TAK** | którykolwiek NIE |

**Regresja pełna:** bramka A + bramka B + M10 + M11 + 10 kroków M12.

---

### Bramka warstwy C — czy mamy działającą aplikację?

To nie jest „kod jest”. To jest: **możesz otworzyć laptopa, odpalić, oglądać, wrócić po restarcie.**

- [ ] Checklist M12 = 10/10
- [ ] Kompas 1–8 = TAK
- [ ] `Analiza.MD` nie złamana: świat żyje sam, UI do wglądu
- [ ] Nikt nie musi znać Pythona, żeby zobaczyć efekt (wystarczy `make dev` + przeglądarka)
- [ ] Świadomy brak: VPS, Throungles full, drapieżniki — nie dziury w MVP

**Jeśli cokolwiek z kompasu jest NIE:** aplikacja nie jest skończona, niezależnie od ładnych sprite’ów. Wróć do kamienia, który ten punkt miał odblokować.

**Warstwa C zamknięta** = lokalne MVP UNKNOWN działa.

---

## 5. Testy automatyczne vs. test oczu

| Co | Narzędzie | Kamienie |
|----|-----------|----------|
| Reguły świata | `pytest` | M1–M6 |
| API kontrakt | `pytest` + `httpx` / `TestClient` | M7, M10 |
| Brak endpointów sprawczych | lista dozwolonych metod w teście | M7 |
| Oglądalność, kamera, klik | ręcznie w przeglądarce | M8–M12 |
| Persistencja procesu | runner + sqlite3 | M6, krok 7 w M12 |

Nie blokujemy M8 czekając na Cypress. Jeden ręczny checklist na koniec wystarczy.

---

## 6. Makefile (kontrakt komend)

Docelowe komendy, które pojawiają się wraz z kamieniami:

```bash
make install     # venv + npm i
make test        # pytest
make backend     # uvicorn :8000
make frontend    # vite :5173
make dev         # oba (np. concurrently albo instrukcja dwóch terminali)
make sim         # headless runner --ticks 1000 --print
make sim-resume  # runner --resume
```

Po M6 `make sim` samo w sobie jest demem Warstwy A.

---

## 7. Świadomie nie w tym MVP (nawet lokalnie)

- Docker, nginx, VPS, 604_800 ticków na siłę
- Speed control, pauza gracza, karmienie
- Particle, glitter, 8 kierunków, 6–8 framów, dust
- Kamienie / pęknięcia / tufty
- Wiele światów równolegle (jeden aktywny wystarczy)
- Konta, dźwięk, drapieżniki

Gdy M12 PASS — dopiero wtedy osobny plan `DEV_VPS.md` / 7-dniowy bieg.

---

## 8. Kolejność plików przy starcie kodu

Zaczynamy od **M0**, nie od Pixi.

1. Szkielet backend + frontend + Makefile (`DEV.md` M0)
2. `simulation/world.py` + runner CLI (M1)
3. Dalej według kamieni: **Sprawdzenie efektu** → **Kontrola kursu** → dopiero następny M
4. Po M6: bramka A. Po M9: bramka B. Po M12: bramka C + kompas 1–8.

Nie wolno „przeskoczyć kontroli, bo i tak wiemy”. Kontrola istnieje po to, żeby nie zbudować działających kawałków, które **nie składają się** w aplikację.

Jeśli kamień nie daje efektu w terminalu albo w oknie — nie jest skończony.  
Jeśli daje efekt, ale kontrola kursu ma STOP — efekt jest w niewłaściwą stronę; cofnij albo wytnij dryf.

---

## 8a. Kiedy świadomie zbaczamy (i jak wrócić)

| Objaw | Co to znaczy | Powrót |
|-------|----------------|--------|
| Chcesz przycisk „daj energię” bo wymierają | balans, nie UI | strojenie jabłek/kosztów w silniku (Analiza §10) |
| Tydzień sprite’ów, silnik bez resume | odwrócona kolejność | wróć do M6 zanim M12 |
| Frontend liczy fizykę sam | dwa światy | wyrzuć logikę z Pixi, zostaw render |
| Docker/VPS w M0–M11 | inny cel niż ten dokument | odłóż do `DEV_VPS.md` |
| Inspector edytuje genom | złamana obietnica wglądu | pole → read-only |

---

## 9. Definition of Done — cały dokument

Lokalne MVP jest skończone, gdy:

1. Silnik sam tyka, je, umiera, rozmnaża, mutuje, uczy się.
2. SQLite przeżywa restart.
3. UI jest obserwatorium: START, viewport, stats, log, inspector, tag/follow.
4. Po START nie da się wpłynąć na świat.
5. Checklist M12 ma 10/10.
6. **Bramki A, B, C i kompas 1–8 są na TAK** — nie tylko ostatni commit.

Tożsamość z `Analiza.MD` zostaje: **świat żyje sam, UI jest do wglądu, wszystko da się odpalić na localhost.**

Skrót na kartce przy kodowaniu:

```
Po każdym M:
  1. Czy widać efekt?          (komenda / ekran)
  2. Czy to zgodne z kamieniem? (nie dobudowaliśmy „przy okazji”)
  3. Który punkt kompasu 1–8?  (musi być choć jeden)
  4. Czy poprzednie PASS żyją? (regresja)
  5. Czy padło któreś STOP?    (przycisk władzy, VPS, ML, drugi silnik w UI)
  → TAK/TAK/TAK/TAK/NIE = następny kamień
  → cokolwiek inaczej = nie idziemy do celu aplikacji
```
