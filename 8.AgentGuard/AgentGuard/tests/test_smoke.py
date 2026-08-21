"""Smoke test: the offline pipeline must run end-to-end without network."""
from agentguard.run_evaluation import main


def test_full_offline_pipeline(tmp_path, monkeypatch):
    # Just make sure the CLI returns 0 with the fake provider.
    exit_code = main(["--provider", "fake"])
    assert exit_code == 0
