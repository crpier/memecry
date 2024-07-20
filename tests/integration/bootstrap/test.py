import os
from pathlib import Path

import pytest
from relax.injection import clear_injections

import memecry.bootstrap


@pytest.fixture()
def _set_dev_env():
    os.environ["ENV"] = "DEV"
    os.environ["DB_FILE"] = "test.db"
    # required configuration
    os.environ["SECRET_KEY"] = "some_secret"
    os.environ["TEMPLATES_DIR"] = "memecry/views"
    os.environ["MEDIA_UPLOAD_STORAGE"] = "test/media"
    yield
    clear_injections()
    Path("test.db").unlink()


@pytest.fixture()
def _set_prod_env():
    os.environ["ENV"] = "PROD"
    os.environ["DB_FILE"] = "test.db"
    # required configuration
    os.environ["SECRET_KEY"] = "some_secret"
    os.environ["TEMPLATES_DIR"] = "memecry/views"
    os.environ["MEDIA_UPLOAD_STORAGE"] = "test/media"
    yield
    clear_injections()
    Path("test.db").unlink()


@pytest.mark.usefixtures(_set_dev_env.__name__)
def test_dev_bootstrap():
    memecry.bootstrap.bootstrap()


@pytest.mark.usefixtures(_set_prod_env.__name__)
def test_prod_bootstrap():
    memecry.bootstrap.bootstrap()
    assert Path("test.db").exists()
