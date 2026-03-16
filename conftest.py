import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--integration", action="store_true", default=False)


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if not config.getoption("--integration"):
        skip = pytest.mark.skip(reason="pass --integration to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip)


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "integration: mark test as integration test")
