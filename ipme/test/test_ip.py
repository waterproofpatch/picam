"""
Test the IP endpoint
"""
import pytest


def test_ip_get(ip_address):
    """
    Test the /ip endpoint (GET)

    :param ip_address: fixture
    """
    print(f"Testing IP get...{ip_address}")