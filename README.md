# Data Pipeline
NASS Quick Stats data is very broad, with tons of slightly varying categories of data even within specific sectors and groups. The goal of this pipeline is to collect and clean specific data to be used by [vt-data-colab](https://github.com/VERSO-UVM/react-vt-data/blob/main/docs/architecture/etl.md).

## Development

Clone repository

```sh
git clone https://github.com/Food-Systems-Research-Institute/data-pipeline.git
cd data-pipeline
```

Set up environment with uv ([uv installation](https://github.com/Food-Systems-Research-Institute/data-pipeline.git)).

```sh
uv sync
```

## Contributions    

Format with [Ruff](https://astral.sh/ruff), lint with [ty](https://docs.astral.sh/ty/).
