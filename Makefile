PYTHON := python3
VENV_DIR := .venv
ifeq ($(wildcard $(VENV_DIR)/bin/python),)
	PY := $(PYTHON)
	PIP := $(PYTHON) -m pip
else
	PY := $(VENV_DIR)/bin/python
	PIP := $(VENV_DIR)/bin/pip
endif

SPHINXBUILD := $(PY) -m sphinx
SOURCEDIR := docs
BUILDDIR := docs/_build
PORT := 8000

.PHONY: help venv install html clean rebuild serve

help:
	@echo "Targets:"
	@echo "  make venv     Create Python virtual environment (.venv)"
	@echo "  make install  Install dependencies from requirements.txt"
	@echo "  make html     Build HTML documentation"
	@echo "  make clean    Remove build output"
	@echo "  make rebuild  Clean and rebuild HTML docs"
	@echo "  make serve    Build and serve docs at http://127.0.0.1:$(PORT)"

venv:
	$(PYTHON) -m venv $(VENV_DIR)

install:
	$(PIP) install -r requirements.txt

html:
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html

clean:
	rm -rf $(BUILDDIR)

rebuild: clean html

serve: html
	$(PY) -m http.server $(PORT) --directory $(BUILDDIR)/html
