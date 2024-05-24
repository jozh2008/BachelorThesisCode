FLAKE8 := flake8
FLAKE8_CONFIG := .github/linters/.flake8  # Change this to the path of your .flake8 configuration file
BLACK :=black

# Specify source files or directories
SRC := *.py

all: compile test format checkstyle 

compile:
	python3 -m py_compile $(SRC)

format:
	$(BLACK) $(SRC)

test:
	python3 -m doctest $(SRC)

checkstyle:
	$(FLAKE8) --config=$(FLAKE8_CONFIG) $(SRC)

clean:
	rm -rf __pycache__
	rm -f *.pyc
	rm -rf Tools/Code/__pycache__
	rm -f Tools/Code/*.pyc
	