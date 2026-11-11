# Makefile del Proyecto Final - Grupo 4 (Paradigmas de Programacion, SIST0176)
CXX      ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -fopenmp
JAVAC    ?= javac
JAVA     ?= java
PYTHON   ?= python3

BUILD    = build
SRC_JAVA = $(shell find java/src -name '*.java')

.PHONY: all cpp java test demo bench clean

all: cpp java

cpp: $(BUILD)/convolve $(BUILD)/bench

$(BUILD)/convolve: cpp/main.cpp cpp/convolucion.cpp cpp/convolucion.hpp cpp/pgm.hpp
	@mkdir -p $(BUILD)
	$(CXX) $(CXXFLAGS) cpp/main.cpp cpp/convolucion.cpp -o $@

$(BUILD)/bench: cpp/bench.cpp cpp/convolucion.cpp cpp/convolucion.hpp
	@mkdir -p $(BUILD)
	$(CXX) $(CXXFLAGS) cpp/bench.cpp cpp/convolucion.cpp -o $@

java: $(SRC_JAVA)
	@mkdir -p $(BUILD)/java
	$(JAVAC) --release 17 -d $(BUILD)/java $(SRC_JAVA)
	@touch $(BUILD)/java.stamp

test: all
	$(PYTHON) -m unittest discover -s funcional/tests -v
	$(JAVA) -cp $(BUILD)/java tac.pruebas.PruebasTac

demo: all
	$(JAVA) -cp $(BUILD)/java tac.app.Main analizar tac_01 --tipo tumoral
	$(JAVA) -cp $(BUILD)/java tac.app.Main lote --hilos 3

bench: cpp
	./$(BUILD)/bench | tee docs/benchmarks.md

clean:
	rm -rf $(BUILD) salida/*.pgm
