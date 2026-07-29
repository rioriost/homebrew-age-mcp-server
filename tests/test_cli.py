import logging
from types import SimpleNamespace

import pytest
from psycopg.conninfo import conninfo_to_dict

import age_mcp_server
from age_mcp_server import _prepare_connection_string


def test_connection_string_is_not_reconstructed_without_azure_identity() -> None:
    connection_string = "host=db.example user=me password='contains spaces'"

    assert _prepare_connection_string(connection_string, False) == connection_string


def test_azure_identity_uses_resolved_cli_and_quotes_token(monkeypatch) -> None:
    monkeypatch.delenv("PGPASSWORD", raising=False)
    monkeypatch.setattr(age_mcp_server.shutil, "which", lambda _name: "/usr/local/bin/az")
    calls = []

    def fake_run(argv, **kwargs):
        calls.append((argv, kwargs))
        return SimpleNamespace(stdout="token with spaces\n")

    monkeypatch.setattr(age_mcp_server.subprocess, "run", fake_run)

    connection_string = _prepare_connection_string(
        "host=db.example user=me", use_azure_identity=True
    )

    assert calls[0][0][0] == "/usr/local/bin/az"
    assert calls[0][1]["timeout"] == 30
    assert conninfo_to_dict(connection_string)["password"] == "token with spaces"


def test_existing_password_skips_azure_cli(monkeypatch) -> None:
    monkeypatch.setattr(
        age_mcp_server.shutil,
        "which",
        lambda _name: pytest.fail("Azure CLI lookup should not occur"),
    )

    connection_string = "host=db.example password=already-present"

    assert _prepare_connection_string(connection_string, True) == connection_string


def test_azure_identity_requires_azure_cli(monkeypatch) -> None:
    monkeypatch.delenv("PGPASSWORD", raising=False)
    monkeypatch.setattr(age_mcp_server.shutil, "which", lambda _name: None)

    with pytest.raises(RuntimeError, match="Azure CLI"):
        _prepare_connection_string("host=db.example user=me", True)


def test_empty_azure_token_is_rejected(monkeypatch) -> None:
    monkeypatch.delenv("PGPASSWORD", raising=False)
    monkeypatch.setattr(age_mcp_server.shutil, "which", lambda _name: "/usr/bin/az")
    monkeypatch.setattr(
        age_mcp_server.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(stdout="\n"),
    )

    with pytest.raises(RuntimeError, match="empty"):
        _prepare_connection_string("host=db.example", True)


def test_cli_forwards_pool_timeout_and_telemetry_options(monkeypatch) -> None:
    calls = {}

    async def fake_main(**kwargs):
        calls.update(kwargs)

    monkeypatch.setattr(age_mcp_server.server, "main", fake_main)
    monkeypatch.setattr(
        age_mcp_server,
        "configure_otel_exporters",
        lambda service_name: calls.update(exporter_service=service_name),
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "age_mcp_server",
            "--pg-con-str",
            "host=db.example",
            "--allow-write",
            "--debug",
            "--statement-timeout-ms",
            "2500",
            "--pool-min-size",
            "2",
            "--pool-max-size",
            "6",
            "--load-age",
            "--enable-telemetry",
            "--otel-service-name",
            "age-test",
        ],
    )

    age_mcp_server.main()

    assert calls["pg_con_str"] == "host=db.example"
    assert calls["allow_write"] is True
    assert calls["log_level"] == logging.DEBUG
    assert calls["statement_timeout_ms"] == 2500
    assert calls["pool_min_size"] == 2
    assert calls["pool_max_size"] == 6
    assert calls["load_age"] is True
    assert calls["exporter_service"] == "age-test"


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        ["--pg-con-str", "host=db.example", "--statement-timeout-ms", "0"],
        [
            "--pg-con-str",
            "host=db.example",
            "--pool-min-size",
            "4",
            "--pool-max-size",
            "2",
        ],
    ],
)
def test_cli_rejects_missing_connection_and_invalid_limits(monkeypatch, arguments) -> None:
    monkeypatch.setattr("sys.argv", ["age_mcp_server", *arguments])

    with pytest.raises(SystemExit, match="2"):
        age_mcp_server.main()
