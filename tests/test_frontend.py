import pytest
from bs4 import BeautifulSoup


@pytest.mark.asyncio
async def test_homepage_returns_html(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]

    soup = BeautifulSoup(resp.text, "html.parser")
    assert soup.title is not None
    assert soup.title.string == "picShare"