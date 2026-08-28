"""Smoke test: verify the package installs and imports cleanly."""
import vollab


def test_package_imports():
    """The package should import without error."""
    assert vollab is not None
