import pytest

def test_about(client):
    response = client.get('/about')
    assert b'About Page' in response.data

def test_home(client):
    response = client.get('/home')
    assert b'Home Page' in response.data