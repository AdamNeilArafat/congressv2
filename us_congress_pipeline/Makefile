.PHONY: init download extract load link metrics export all

init:
python -m pipeline.cli init

download:
python -m pipeline.cli download --congresses $(CONGRESSES) --cycles $(CYCLES)

extract:
python -m pipeline.cli extract

load:
python -m pipeline.cli load

link:
python -m pipeline.cli link

metrics:
python -m pipeline.cli metrics --cycles $(CYCLES) --congresses $(CONGRESSES)

export:
python -m pipeline.cli export --out data/outputs/

all: init download extract load link metrics export
