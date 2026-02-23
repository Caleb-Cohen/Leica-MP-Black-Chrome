"""Shared test fixtures."""

import pytest


@pytest.fixture
def camerawest_config():
    return {
        "camerawest_search_url": "https://camerawest.com/search/suggest.json",
        "camerawest_search_query": "leica mp",
        "camerawest_base_url": "https://camerawest.com/products/",
    }


@pytest.fixture
def mapcamera_config():
    return {
        "mapcamera_search_url": "https://www.mapcamera.com/search",
        "mapcamera_search_keyword": "leica mp",
        "mapcamera_base_url": "https://www.mapcamera.com",
    }


@pytest.fixture
def fredmiranda_config():
    return {
        "fredmiranda_forum_url": "https://www.fredmiranda.com/forum/board/10/",
        "fredmiranda_base_url": "https://www.fredmiranda.com",
    }
