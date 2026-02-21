# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

E2E test automation framework for the TIR (E2E Networks) GPU infrastructure management API. Tests cover GPU instance (notebook) lifecycle, dataset management, shared file systems (SFS), and reserved IP allocation.

## Commands

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure credentials for your target environment
# Edit env/prod.env or env/groot.env with:
#   BEARER_TOKEN, API_KEY, PROJECT_ID, TEAM_ID
```

### Running Tests

```bash
# Run all tests against a specific environment
ENV=prod pytest

# Run by resource marker
ENV=prod pytest -m instance
ENV=prod pytest -m dataset

# Run a specific test file
ENV=prod pytest tests/api/instance/instance_test.py

# Run a single test function
ENV=prod pytest tests/api/instance/instance_test.py::test_overview

# Run with Allure reporting
ENV=prod pytest --alluredir=allure-results

# Run tests in parallel
ENV=prod pytest -n auto
```

The `ENV` variable selects the config pair: `tests/config/{ENV}.yaml` + `env/{ENV}.env`. Valid values: `prod`, `groot`, `loki`.

## Architecture

### Request Flow

```
Test → conftest fixtures (api_client, config) → BaseApiClient → TIR REST API
                                                     ↑
                                               paths.py (endpoint definitions)
```

### Layer Responsibilities

| Layer | Path | Purpose |
|-------|------|---------|
| Config | `tests/config/`, `env/` | YAML + dotenv credential loading |
| Client | `tests/clients/base_api_client.py` | HTTP requests with auth headers (Bearer token + API key injected automatically) |
| Endpoints | `tests/api/paths.py` | Central registry of all URL path templates |
| Helpers | `tests/api/{resource}/helper.py` | Lifecycle operations + polling for async state changes |
| Payloads | `tests/payloads/` | Request body builders with defaults |
| Fixtures | `tests/fixtures/` | Module-scoped resource setup/teardown (create → yield id → delete) |
| Assertions | `tests/assertions/common_assert.py` | `assert_response_exists()` and `assert_schema()` |
| Schemas | `tests/schemas/` | JSON Schema Draft 7 files for response validation |

### Key Design Patterns

**Async polling**: Instance and dataset operations are asynchronous. Helpers like `ensure_status()` and `ensure_dataset_ready()` poll until the resource reaches the desired state. Always use these instead of checking status once.

**Module-scoped fixtures**: Each test module shares a single resource (one instance, one dataset, etc.) created at module start and destroyed at module end. Tests must not delete the shared resource.

**Environment configuration**: `conftest.py::pytest_sessionstart` loads the env file based on `ENV`, then creates `config` and `api_client` session-scoped fixtures available to all tests.

**Endpoint format**: All endpoints in `paths.py` use `.format(team_id=..., project_id=..., ...)` for path parameters. Query parameters (`apikey`, `location`) are injected by `BaseApiClient` automatically.

### Adding New Resource Tests

1. Add endpoint paths to `tests/api/paths.py`
2. Create helper functions in `tests/api/{resource}/helper.py`
3. Create payload builder in `tests/payloads/{resource}_payloads.py`
4. Add JSON schema files to `tests/schemas/{resource}/`
5. Create module-scoped fixture in `tests/fixtures/{resource}.py`
6. Write tests in `tests/api/{resource}/{resource}_test.py` with `@pytest.mark.{resource}`

## Environment Variables

Required in `env/{ENV}.env`:

```
BEARER_TOKEN   # API auth token
API_KEY        # API key appended to all requests as query param
PROJECT_ID     # Project scope for API paths
TEAM_ID        # Team scope for API paths
```
