"""Unit tests for semp/client.py (mocked requests.Session)."""

import pytest
import requests

from semp_workflow.exceptions import SEMPError
from semp_workflow.semp.client import NOT_FOUND, SempClient


@pytest.fixture
def client(mocker):
    """SempClient with a mocked requests.Session.

    We create a real SempClient (so __init__ runs normally and sets up
    session.headers etc.), then replace the session with a plain MagicMock
    so all network calls are intercepted.
    """
    c = SempClient(
        host="https://broker:943",
        username="admin",
        password="secret",
        msg_vpn="default",
        verify_ssl=False,
    )
    mock_session = mocker.MagicMock()
    c.session = mock_session
    return c, mock_session


def _make_response(mocker, status_code=200, json_body=None, text=""):
    resp = mocker.MagicMock()
    resp.status_code = status_code
    resp.text = text if json_body is None else "body"
    resp.json.return_value = json_body or {}
    return resp


class TestVpnUrl:
    def test_basic(self, client):
        c, _ = client
        assert c.vpn_url == "https://broker:943/SEMP/v2/config/msgVpns/default"

    def test_vpn_encoded(self):
        c = SempClient("https://b", "u", "p", "my/vpn")
        assert "my%2Fvpn" in c.vpn_url


class TestEnc:
    def test_slash(self):
        assert "/" not in SempClient._enc("a/b")

    def test_hash(self):
        assert "#" not in SempClient._enc("#DEAD")

    def test_alphanumeric(self):
        assert SempClient._enc("abc") == "abc"


class TestRequest:
    def test_success_returns_data(self, client, mocker):
        c, session = client
        session.request.return_value = _make_response(
            mocker,
            json_body={"meta": {"responseCode": 200}, "data": {"key": "val"}},
            text="body",
        )
        result = c._request("GET", "queues/myq")
        assert result == {"key": "val"}

    def test_empty_body_returns_none(self, client, mocker):
        c, session = client
        resp = mocker.MagicMock()
        resp.status_code = 200
        resp.text = ""
        session.request.return_value = resp
        result = c._request("DELETE", "queues/myq")
        assert result is None or result == {}

    def test_semp_error_raises(self, client, mocker):
        c, session = client
        session.request.return_value = _make_response(
            mocker,
            json_body={
                "meta": {
                    "responseCode": 400,
                    "error": {"description": "Bad request", "code": 99},
                }
            },
            text="body",
        )
        with pytest.raises(SEMPError) as exc_info:
            c._request("POST", "queues")
        assert exc_info.value.semp_code == 99

    def test_connection_error_raises_semp_error(self, client):
        c, session = client
        session.request.side_effect = requests.ConnectionError("refused")
        with pytest.raises(SEMPError) as exc_info:
            c._request("GET", "queues")
        assert exc_info.value.status_code == 0

    def test_timeout_raises_semp_error(self, client):
        c, session = client
        session.request.side_effect = requests.Timeout()
        with pytest.raises(SEMPError) as exc_info:
            c._request("GET", "queues")
        assert exc_info.value.status_code == 0

    def test_request_exception_raises_semp_error(self, client):
        c, session = client
        session.request.side_effect = requests.RequestException("generic")
        with pytest.raises(SEMPError):
            c._request("GET", "queues")


class TestExists:
    def test_found_returns_true_and_data(self, client, mocker):
        c, session = client
        data = {"queueName": "myq"}
        session.request.return_value = _make_response(
            mocker,
            json_body={"meta": {"responseCode": 200}, "data": data},
            text="body",
        )
        found, result = c.exists("queues/myq")
        assert found is True
        assert result == data

    def test_not_found_semp_code_returns_false(self, client, mocker):
        c, session = client
        session.request.return_value = _make_response(
            mocker,
            json_body={
                "meta": {
                    "responseCode": 400,
                    "error": {"description": "Not found", "code": NOT_FOUND},
                }
            },
            text="body",
        )
        found, result = c.exists("queues/missing")
        assert found is False
        assert result is None

    def test_404_status_returns_false(self, client, mocker):
        c, session = client
        session.request.return_value = _make_response(
            mocker,
            json_body={
                "meta": {
                    "responseCode": 404,
                    "error": {"description": "Not found", "code": 0},
                }
            },
            text="body",
        )
        found, result = c.exists("queues/missing")
        assert found is False

    def test_other_error_reraises(self, client, mocker):
        c, session = client
        session.request.return_value = _make_response(
            mocker,
            json_body={
                "meta": {
                    "responseCode": 500,
                    "error": {"description": "Server error", "code": 99},
                }
            },
            text="body",
        )
        with pytest.raises(SEMPError):
            c.exists("queues/myq")


class TestConnectionMethod:
    def test_returns_true_on_200(self, client, mocker):
        c, session = client
        resp = mocker.MagicMock()
        resp.status_code = 200
        session.get.return_value = resp
        assert c.test_connection() is True

    def test_returns_false_on_non_200(self, client, mocker):
        c, session = client
        resp = mocker.MagicMock()
        resp.status_code = 401
        session.get.return_value = resp
        assert c.test_connection() is False

    def test_returns_false_on_request_exception(self, client):
        c, session = client
        session.get.side_effect = requests.RequestException("refused")
        assert c.test_connection() is False


class TestCrudMethods:
    def test_create_calls_post(self, client, mocker):
        c, session = client
        session.request.return_value = _make_response(
            mocker,
            json_body={"meta": {"responseCode": 200}, "data": {}},
            text="body",
        )
        c.create("queues", {"queueName": "q"})
        call_args = session.request.call_args
        assert call_args[0][0] == "POST"

    def test_update_calls_patch(self, client, mocker):
        c, session = client
        session.request.return_value = _make_response(
            mocker,
            json_body={"meta": {"responseCode": 200}, "data": {}},
            text="body",
        )
        c.update("queues/q", {"owner": "u"})
        call_args = session.request.call_args
        assert call_args[0][0] == "PATCH"

    def test_delete_calls_delete(self, client, mocker):
        c, session = client
        resp = mocker.MagicMock()
        resp.status_code = 200
        resp.text = ""
        session.request.return_value = resp
        c.delete("queues/q")
        call_args = session.request.call_args
        assert call_args[0][0] == "DELETE"
