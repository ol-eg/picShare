from starlette.requests import Request


def _make_request() -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "query_string": b"",
        "scheme": "http",
        "server": ("test", 80),
        "client": ("127.0.0.1", 1),
        "root_path": "",
    }
    return Request(scope)


def test_render_home_returns_html():
    from starlette.responses import Response

    from app.views import render_home

    resp = render_home(_make_request())
    assert isinstance(resp, Response)
    assert "text/html" in resp.headers["content-type"]


def test_render_login_and_register_return_html():
    from app.views import render_login, render_register

    for fn in (render_login, render_register):
        resp = fn(_make_request())
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]


def test_render_register_error_status_code():
    from app.views import render_register_error

    resp = render_register_error(_make_request(), "boom")
    assert resp.status_code == 400


def test_redirect_home_status_and_location():
    from app.views import redirect_home

    resp = redirect_home()
    assert resp.status_code == 303
    assert resp.headers["location"] == "/"
