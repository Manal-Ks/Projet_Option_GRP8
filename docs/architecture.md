# Project architecture

Overview of the main components:

- `demo_dev_run.py`: demo runner that loads data and runs the pipeline.
- `src/schema.py`: data schema and validation helpers.
- `src/preprocessing.py`: parsing and normalization entry points. Uses specific normalizers:
  - `src/education.py`
  - `src/languages.py`
  - `src/skills.py`
  - `src/sector.py`
- `src/data_quality.py`: small data-quality metrics.
- `src/pairing.py`: pairing logic (cartesian and filtered by sector).

Data flow:

1. Validate & coerce inputs via `schema.py`.
2. Preprocess and normalize fields in `preprocessing.py`.
3. Produce quality reports via `data_quality.py`.
4. Build candidate-job pairs in `pairing.py`.
