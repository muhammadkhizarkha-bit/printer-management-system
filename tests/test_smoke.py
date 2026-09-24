"""Basic smoke tests for the Printer Management System."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    # `with` triggers the lifespan (creates tables, seeds admin & printers).
    with TestClient(app) as c:
        yield c


def test_root_redirects_to_login(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code in (302, 303, 307)
    assert "/login" in r.headers["location"]


def test_login_page_renders(client):
    r = client.get("/login")
    assert r.status_code == 200
    assert "Welcome back" in r.text


def test_signup_page_renders(client):
    r = client.get("/signup")
    assert r.status_code == 200
    assert "Create your account" in r.text


def test_admin_can_login(client):
    r = client.post(
        "/login",
        data={"email": "admin@printer.com", "password": "Admin@123"},
        follow_redirects=False,
    )
    assert r.status_code in (302, 303)
    assert "access_token" in r.cookies


def test_dashboard_requires_auth():
    with TestClient(app) as fresh:
        r = fresh.get("/dashboard", follow_redirects=False)
        assert r.status_code in (401, 302, 303)
