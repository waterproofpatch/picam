"""
Test the IP endpoint
"""
import pytest


def test_ip_post(client):
    response = client.post("/ip", json={"ip": "1.2.3.4"})
    assert 200 == response.status_code


def test_ip_get(client):
    response = client.get("/ip")
    assert 200 == response.status_code
    assert [] == response.json
