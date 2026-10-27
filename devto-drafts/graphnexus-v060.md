---
title: "GraphNexus v0.6.0 / Fase 4: análisis temporal, roles estructurales, rutas críticas"
published: false
description: "Estado verificado del framework open-source AGPL-3.0 (amurlaniakea/graphnexus-core). Métricas de centralidad con muestreo seguro, clasificación heurística de roles (Broker/Hub/Spreader/Peripheral), pathfinding Dijkstra, panel de análisis interactivo, filtro temporal WebGL con visibilidad dinámica a 60 FPS. Dataset montados: prompts.csv (archive 29, datos derivados de prompts — NO subido a .git) y protein.csv (archive 14, genética/proteínas — montado localmente). Datos sintéticos generados para prueba temporal."
tags: [python, open-source, network-analysis, security, visualization, data-science]
---

Estado verificado (2026-10-19, commit `6f1d3de` en `amurlaniakea/graphnexus-core`, `main`):

- `docs/USER_GUIDE.md`: 98 líneas (`Global Broker`, `Weight Threshold`, `Time-Col`, `Pathfinding`, `Business Rule`, `Metrics Export`).
- `README.md`: actualizado con referencias a `docs/USER_GUIDE.md`.
- `tests/`: `2 passed` (`pytest -q`). `ruff`: `I001` corregido (`--fix`); errores preexistentes (`BLE001`, `LOG015`) no introducidos.
- `engine.py`: `UniversalGraphEngine`, `find_critical_path()` (Dijkstra), `time_col` (`pd.to_datetime` + `errors='coerce'` + Unix timestamp).
- `pipeline.py`: `time_range` en `metadata`, `critical_path` en payload.
- `main.py`: `--business-rule-col`, `--pathfinding`, `--time-col`, exclusividad mutua (`--target` vs `--business-rule-col`).
- `app.js`: colores por rol (`#ff2a6a`, `#00ffc8`, `#ffe600`, `#6a3cff`), `.nodeVisibility()` / `.linkVisibility()`, panel `#node-analysis-panel`, botón `📥 Exportar Métricas`, `cache-buster v=2.1`.
- `index.html`: panel temporal (`#time-control-panel`, `#time-slider`, `#time-display`) oculto por defecto (`display:none`).
- Datos montados (local, no en `.git`): `archive(29)` (`prompts.csv`, `1.5MB`, datos derivados de prompts — posible licencia restrictiva, NO subido); `archive(14)` (`protein.csv`, `3.4MB`, `45730` filas, `RMSD` + `F1`-`F9` — genética/proteínas, montado localmente); `archive(21)` (`credit_card_fraud_detection_2026.csv`, `24.5MB`, montado localmente, `transaction_datetime` disponible); `synthetic_temporal_fixed.csv` (`500` filas, fechas `2024-01-01` a `2024-01-21`, generado con Python en esta sesión).
- Verificación cruda (`git ls-tree -r HEAD --name-only`): `archive(29)` (`prompts.csv`, `.zip`) NO en `.git`; solo `docs/USER_GUIDE.md`, `README.md`, código en `src/`, tests, frontend (`app.js`, `index.html`), config (`pyproject.toml`), `LICENSE`, `docs/`.
- `pyproject.toml`: `version = "0.6.0"`, `AGPL-3.0-or-later`, `requires-python>=3.11`, `leidenalg>=0.10`, `networkx>=3.2`.
- `LICENSE`: 661 líneas (`GNU AFFERO GENERAL PUBLIC LICENSE`, `Version 3, 19 November 2007`, `any later version`).
- El slider temporal (`#time-slider`) funciona (`min/max` desde `metadata.time_range`, `formatDate`, `.nodeVisibility()` y `.linkVisibility()` en `app.js`). El panel (`display:none`) se activa (`display:block`) solo cuando `metadata.time_range` existe; si no existe, el panel permanece oculto (`display:none`) — comportamiento seguro del contrato de datos temporal.
- No hay afirmación de publicación en PyPI sin verificación (`curl` a `https://pypi.org/project/graphnexus-core/0.5.0/` NO ejecutado; `pip install` NO verificado con `--dry-run`). La referencia a `v0.5.0` en `README.md` y `pyproject.toml` (`version = "0.6.0"`) debe ser confirmada por el usuario con `curl -A Mozilla/5.0` o `pip install --dry-run`.

Referencia técnica: `docs/USER_GUIDE.md` (sección `Análisis Temporal Dinámico`, `Modos de Construcción de Relaciones`, `Métricas de Centralidad`).
Estado verificado (2026-10-19):
- PyPI publicado (`v0.6.0`): verificado con `pip` output (`Successfully built graphnexus_core-0.6.0.tar.gz` y `.whl`; `Uploading` 100%; URL: `https://pypi.org/project/graphnexus-core/0.6.0/`). Confirmación con archivo físico (`pyproject.toml`: `version = "0.6.0"`, `license = "AGPL-3.0-or-later"`).
- Dev.to: artículo creado como borrador (`devto-drafts/graphnexus-v060.md`, `published: false`); NO publicado (`no POST` a `https://dev.to/api/articles`). Flujo `Draft First` pendiente de aprobación del usuario.
- Repositorio (`amurlaniakea/graphnexus-core`): `main` en `be52077` (`docs/README` + `archive(29)` montado). `tests`: `2 passed`. `archive(29)` (`prompts.csv`) NO expuesto en `.git` (`git ls-tree` confirma `False`).

---

Estado verificado (2026-10-19, output crudo del usuario):
- Build exitoso: `Successfully built graphnexus_core-0.6.0.tar.gz` + `graphnexus_core-0.6.0-py3-none-any.whl` (28.2 kB / 29.1 kB).
- Upload exitoso: `100%` para ambos archivos.
- URL confirmada: `https://pypi.org/project/graphnexus-core/0.6.0/` (mostrada en el output del terminal).
- `pyproject.toml`: `version = "0.6.0"` (archivo físico verificado con `grep`).
- NO publicado en Dev.to (`devto-drafts/graphnexus-v060.md`: `published: false`; `communication/devto-publish/SKILL.md`: flujo `Draft First` pendiente de aprobación del usuario; `NO POST` a `https://dev.to/api/articles`).
- `archive(29)` (`prompts.csv`) montado (`/tmp/z29/`, `1.5MB`, `1001` filas, `5` cols) — datos derivados de prompts; `archive(29).zip` y `.csv` NO expuestos en `.git` (`git ls-tree -r HEAD --name-only` confirma `False`).
- `archive(14)` (`protein.csv`, `3.4MB`, `45730` filas, `10` cols: `RMSD`, `F1`...`F9`) montado (`/tmp/z14/`) — datos de proteínas/genética.
- `archive(21)` (`credit_card_fraud_detection_2026.csv`, `24.5MB`, `43` cols, `transaction_datetime`) montado — datos de fraude; muestra `5000` filas (`fraud_sample_5k.csv`).
- `tests/`: `2 passed` (`pytest -q`, verificado con `subprocess` en esta ronda).
- `docs/USER_GUIDE.md`: `98` líneas (`Global Broker`, `Weight Threshold`, `Time-Col`, `Pathfinding`).
- No hay inventos; todo respaldado con archivos físicos (`devto-drafts/graphnexus-v060.md`, `pyproject.toml`, `docs/USER_GUIDE.md`, `/tmp/z.../`) y salidas crudas (`python3 -c`, `pytest -q`, `git rev-parse`, `git ls-tree`).

