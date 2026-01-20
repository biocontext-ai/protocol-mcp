import protocol_mcp


def test_package_has_version():
    """Testing package version exist."""
    assert protocol_mcp.__version__ is not None
