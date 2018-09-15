import pytest
from werkzeug.exceptions import Forbidden, InternalServerError

def test_404_error(client):
	response = client.get('/abcdefg')
	assert b'Oops. Page Not Found (404)' in response.data


def test_403_error(app):
	with app.test_request_context():
		response = app.handle_http_exception(Forbidden())
		assert "You don't have permission" in response[0]

def test_500_error(app):
	with app.test_request_context():
		response = app.handle_http_exception(InternalServerError())
		assert "Oops. Something went wrong. (500)" in response[0]

