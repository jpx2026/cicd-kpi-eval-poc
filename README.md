# Illustrative CI/CD Proof-of-Concept (`demo-cicd`)

Controlled proof-of-concept comparing two GitHub Actions configurations over 15 commits:

- **Pipeline A (`.github/workflows/pipeline-a.yml`)**: Vanity/speed-optimized (`ruff` and `bandit` wrapped in `continue-on-error: true`, integration tests skipped).
- **Pipeline B (`.github/workflows/pipeline-b.yml`)**: Quality-gated (strict `ruff` and `bandit`, unit tests, and 15-seed randomized integration suite).

## Suggested 15-Commit Workload

Push the following 15 commits sequentially to observe how Pipeline A and Pipeline B diverge:

1. **C01 (Baseline)**: Initial clean repository (`src/`, `tests/`, `.github/workflows/`). Both pass.
2. **C02 (Clean feature)**: Add `discount_cap` helper in `src/pipeline_app.py` with unit test. Both pass.
3. **C03 (Lint smell)**: Introduce unused import and style violation in `src/pipeline_app.py`. A: green (masked); B: fails `ruff`.
4. **C04 (Fix lint)**: Clean up C03. Both pass.
5. **C05 (Security anti-pattern)**: Add `subprocess.run(cmd, shell=True)` helper in `src/pipeline_app.py`. A: green (masked by `continue-on-error`); B: fails `bandit`.
6. **C06 (Fix security)**: Replace `shell=True` with argument list. Both pass.
7. **C07 (Integration contract break)**: Change `AUDIT_LOG` prefix from `ORDER_CONFIRMED:` to `CONFIRMED:`. A: green (skips integration); B: fails `test_order_to_audit_pipeline`.
8. **C08 (Fix contract)**: Restore prefix. Both pass.
9. **C09 (README-only commit)**: Update `README.md` only (tests infrastructure/non-code trigger behavior). Both run; observe wasted compute / any spurious runner failure.
10. **C10 (Tighten async timing)**: Lower `time.sleep(0.25)` in `test_async_dispatch_timing_sensitivity` to `0.19` (near `5 * 0.04 = 0.20s`). A: green; B: intermittently fails across 15 seeds (flaky async wait).
11. **C11 (Order-dependent shared state)**: Remove `AUDIT_LOG.clear()` in `test_order_to_audit_pipeline` while `test_audit_log_isolation` runs first under some seeds. A: green; B: fails under order-dependent seeds.
12. **C12 (Fix flaky tests)**: Replace `time.sleep(...)` with `bus.flush()` and restore `AUDIT_LOG.clear()`. Both pass deterministically.
13. **C13 (Production rounding bug)**: Introduce negative `tax_rate` or subtle rounding regression only caught in integration assertion. A: green; B: fails integration.
14. **C14 (Fix production bug)**: Restore correct rounding and validation. Both pass.
15. **C15 (Refactor cleanup)**: Refactor `LineItem` formatting cleanly. Both pass.

After pushing C01–C15 to a GitHub repository, record each workflow's mean duration, apparent build success rate, suppressed/caught defects, and flaky restarts into Table III of `paper-ieee/main.tex`.

<!-- C09: doc-only update triggering full CI -->
