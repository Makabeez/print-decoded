# Rebuild everything from Pacifica's public API (no keys, no wallet). Needs python3 + numpy.
reproduce:
	python3 scripts/pull.py
	python3 scripts/iv.py
	python3 scripts/export.py
	python3 scripts/build.py
site:
	python3 scripts/build.py
.PHONY: reproduce site
