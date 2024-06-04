FLAKE8 := flake8
FLAKE8_CONFIG := .github/linters/.flake8  # Change this to the path of your .flake8 configuration file
BLACK :=black

CODE := Tools/Code

TEST := tests

# Specify source files or directories
SRC := *.py

VENV_DIR := .venv
REQUIREMENTS := requirements.txt
VENV_PYTHON := python3

DEV_REQUIREMENTS := dev-requirements.txt

all: install compile test format checkstyle 

. $(VENV_DIR)/bin/activate: $(REQUIREMENTS) $(DEV_REQUIREMENTS)
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv $(VENV_DIR); \
	fi
	@if [ $(REQUIREMENTS) -nt $(VENV_DIR)/requirements.installed ]; then \
		echo "Installing requirements..."; \
		. $(VENV_DIR)/bin/activate && pip install -r $(REQUIREMENTS); \
		touch $(VENV_DIR)/requirements.installed; \
	else \
		echo "Requirements have not changed, skipping installation."; \
	fi
	@if [ $(DEV_REQUIREMENTS) -nt $(VENV_DIR)/dev-requirements.installed ]; then \
		echo "Installing dev-requirements..."; \
		. $(VENV_DIR)/bin/activate && pip install -r $(DEV_REQUIREMENTS); \
		touch $(VENV_DIR)/dev-requirements.installed; \
	else \
		echo "Dev-requirements have not changed, skipping installation."; \
	fi
	@echo "Dependencies are set up."

install: $(VENV_DIR)/bin/activate

compile: install
	python3 -m py_compile $(SRC)

format: install
	$(BLACK) $(SRC)
	$(BLACK) $(CODE) $(SRC)
	$(BLACK) $(TEST) $(SRC)

test: install
	pytest $(TEST) $(SRC)

checkstyle: install
	$(FLAKE8) --config=$(FLAKE8_CONFIG) $(SRC)
	$(FLAKE8) --config=$(FLAKE8_CONFIG) $(CODE) $(SRC)
	$(FLAKE8) --config=$(FLAKE8_CONFIG) $(TEST) $(SRC)

clean:
	rm -rf __pycache__
	rm -f *.pyc
	rm -rf Tools/Code/__pycache__
	rm -f Tools/Code/*.pyc
	