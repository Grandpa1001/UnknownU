.PHONY: install test backend frontend dev sim sim-move sim-life sim-extinct sim-evo sim-learn

BACKEND := backend
FRONTEND := frontend
PY := $(BACKEND)/.venv/bin/python
PIP := $(BACKEND)/.venv/bin/pip
UVICORN := $(BACKEND)/.venv/bin/uvicorn
PYTEST := $(BACKEND)/.venv/bin/pytest

install:
	python3 -m venv $(BACKEND)/.venv
	$(PIP) install -r $(BACKEND)/requirements.txt
	cd $(FRONTEND) && npm install

test:
	cd $(BACKEND) && .venv/bin/pytest

backend:
	cd $(BACKEND) && .venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	cd $(FRONTEND) && npm run dev

dev:
	@echo "Uruchom dwa terminale:"
	@echo "  make backend"
	@echo "  make frontend"
	@echo "Potem: http://127.0.0.1:8000/health  i  http://127.0.0.1:5173"

sim:
	cd $(BACKEND) && .venv/bin/python -m app.simulation.runner --ticks 10 --seed 1 --print

sim-move:
	cd $(BACKEND) && .venv/bin/python -m app.simulation.runner --ticks 100 --seed 1 --print-every 20

sim-life:
	cd $(BACKEND) && .venv/bin/python -m app.simulation.runner --ticks 2000 --seed 1 --print-every 200 --print-events

sim-extinct:
	cd $(BACKEND) && .venv/bin/python -m app.simulation.runner --ticks 5000 --seed 1 --no-apples --print-events --print

sim-evo:
	cd $(BACKEND) && .venv/bin/python -m app.simulation.runner --ticks 8000 --seed 42 --organisms 5 --print-events

sim-learn:
	cd $(BACKEND) && .venv/bin/python -m app.simulation.runner --ticks 3000 --seed 7 --print-events --print-memory org_1
