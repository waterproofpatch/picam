"""
Test the IP endpoint
"""
import pytest


def test_ip_get(client):
    assert 200 == client.get("/ip").status_code
