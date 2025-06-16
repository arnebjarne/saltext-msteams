from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from saltext.msteams.modules import msteams

# from salt.modules import config


@pytest.fixture
def configure_loader_modules(autouse=True):
    return {msteams: {}}


def test_post_card():
    http_ret = {"status": 200}
    http_mock = MagicMock(return_value=http_ret)
    with patch("salt.utils.http.query", http_mock):
        ret = msteams.post_card("test")
        assert ret
        http_mock.assert_called_once_with(
            "https://example.com/web_hook",
            method="POST",
            header_dict={"Content-Type": "application/json"},
            data='{"text": "test", "title": null, "themeColor": null}',
            status=True,
        )
