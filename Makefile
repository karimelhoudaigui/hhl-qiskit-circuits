PYTHON ?= python3

.PHONY: install demo figures test latex clean

install:
	$(PYTHON) -m pip install -r requirements.txt

demo:
	$(PYTHON) scripts/run_hhl_demo.py

figures:
	$(PYTHON) scripts/generate_figures.py

test:
	$(PYTHON) -m pytest

latex:
	$(PYTHON) scripts/compile_latex.py

clean:
	rm -rf .pytest_cache .ruff_cache build dist src/*.egg-info
