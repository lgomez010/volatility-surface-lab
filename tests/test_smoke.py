"""Smoke test: verify the package installs and imports cleanly."""
import src


def test_package_imports():
    """The package should import without error."""
    assert src is not None
