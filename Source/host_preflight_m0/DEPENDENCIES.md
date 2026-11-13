# Dependency and provenance review

Runtime: Python standard library only. Source and tests were authored for TASK-001;
no code/assets from ESP-FLUTTER or SDIY reference repositories were copied.
Approved project schemas/fixtures are read from the repository by tests/callers,
not altered or fetched by the library.

Exact pins in `pyproject.toml` include all test/build transitive dependencies on
Python 3.11. Installed wheel metadata and bundled license texts were inspected.
These permissive tool licenses do not introduce a copyleft requirement on the
project's authored runtime. This review does not select a project source license.

| Package | Version | License |
|---|---|---|
| pytest | 8.3.5 | MIT |
| jsonschema | 4.26.0 | MIT |
| attrs | 25.3.0 | MIT |
| jsonschema-specifications | 2025.9.1 | MIT |
| referencing | 0.36.2 | MIT |
| rpds-py | 0.27.1 | MIT |
| typing-extensions | 4.15.0 | PSF-2.0 |
| colorama | 0.4.6 | BSD-3-Clause |
| iniconfig | 2.1.0 | MIT |
| packaging | 25.0 | Apache-2.0 OR BSD-2-Clause |
| pluggy | 1.6.0 | MIT |
| build | 1.2.2.post1 | MIT |
| pyproject-hooks | 1.2.0 | MIT |
| setuptools | 80.9.0 | MIT |
| wheel | 0.45.1 | MIT |

`pip` is bootstrap tooling supplied by the existing interpreter/venv; its actual
version is recorded in the environment evidence. It is not a package runtime
dependency. Dependencies are installed locally, not vendored or redistributed
inside this library's wheel. Dependency licenses must remain with those packages
if a future deliverable redistributes them.
