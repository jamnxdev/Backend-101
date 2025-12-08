from multidict import CIMultiDict

from proxy.main import strip_hop_by_hop_headers

def test_strip_hop_by_hop_header_removes_standard_and_connection_listed():
    headers = CIMultiDict(
        {
            "Connection": "keep-alive, Upgrade, X-Test-Hop",
            "Keep-Alive": "timeout=5",
            "Upgrade": "h2c",
            "X-Test-Hop": "foo",
            "Host": "example.com",
            "X-Normal": "value",
        }
    )

    cleaned = strip_hop_by_hop_headers(headers)

    assert "Connection" not in cleaned
    assert "Keep-Alive" not in cleaned
    assert "Upgrade" not in cleaned

    assert "X-Test-Hop" not in cleaned

    assert cleaned["Host"] == "example.com"
    assert cleaned["X-Normal"] == "value"