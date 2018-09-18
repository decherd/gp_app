import pytest
from flask import g, session
from flask_login import current_user
from gp_app.models import User
from wtforms.validators import ValidationError
from gp_app.users.utils import send_reset_email


def test_register(client, app):
    assert client.get('/register').status_code == 200
    response = client.post(
        '/register', data={'email': 'other@othercompany.com', 
                        'password': 'testing',
                        'confirm_password': 'testing',
                        'username': 'other'}
    )
    assert 'http://localhost/login' == response.headers['Location']

    with app.app_context():
        assert User.query.filter_by(username='other').first() is not None


def test_redirect_with_login(client, auth):
    auth.login()
    response = client.get('/register')
    assert response.headers['Location'] == 'http://localhost/home'
    response = client.get('/login')
    assert response.headers['Location'] == 'http://localhost/home'


@pytest.mark.parametrize(('username', 'email', 'password', 'confirm_password'), (
    ('other', 'test@mycompany.com', 'test', 'test'),
    ('test', 'other@other.com', 'test', 'test'),
))
def test_register_validate_error(client, username, email, password, confirm_password):
    response = client.post(
        '/register', data={'email': email, 
                    'password': password,
                    'confirm_password': confirm_password,
                    'username': username}
        )
    assert b'Please choose a different one.' in response.data



def test_login(client, auth):
    assert client.get('/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/home'

    with client:
        client.get('/home')
        assert current_user.is_authenticated == True
        assert current_user.id == 1
        assert current_user.username == 'test'


@pytest.mark.parametrize(('email', 'password', 'message'), (
    ('wrong@wrong.com', 'test', b'Login Unsuccessful.'),
    ('test@mycompnay.com', 'a', b'Login Unsuccessful.'),
))
def test_login_validate_input(auth, email, password, message):
    response = auth.login(email, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert current_user.is_authenticated == False


def test_update_account(auth, client):
    response = client.get('/account')
    assert response.headers['Location'] == 'http://localhost/login?next=%2Faccount'

    auth.login()
    response = client.get('account')
    assert b'Account' in response.data


@pytest.mark.parametrize(('email', 'username', 'message'), (
    ('a12345@mycompany.com', 'test', b'That email is taken.'),
    ('test@mycompany.com', 'a12345', b'That username is taken.'),
    ('other@other.com', 'other', b'Your account has been updated!'),
))
def test_update_account_form_validation(auth, client, email, username, message):
    auth.login()
    response = client.post(
        '/account', data={'email': email, 
                    'username': username}, follow_redirects=True
        )
    assert message in response.data


def test_get_verify_reset_token(app):
    with app.app_context():
        user = User.query.first()
        token = user.get_reset_token()
        token2 = token + 'abc'
        user = User.verify_reset_token(token)
        assert user.id == 1
        user = User.verify_reset_token(token2)
        assert user is None


def test_send_reset_email(app):
    with app.app_context(), app.test_request_context():
        user = User.query.first()
        outbox = send_reset_email(user)
        assert len(outbox) == 1
        assert outbox[0].subject == 'Password Reset Request'


def test_reset_request(client, auth):
    response = client.post(
        '/reset_password', data={'email': 'junk@mycompany.com'}, follow_redirects=True
    )
    assert b'There is no account with that email.' in response.data

    response = client.post(
        '/reset_password', data={'email': 'test@mycompany.com'}, follow_redirects=True
    )
    assert b'An email has been sent' in response.data

    auth.login()
    response = client.get('/reset_password')
    assert response.headers['Location'] == 'http://localhost/home'


def test_reset_token(app, client, auth):
    response = client.get(
        '/reset_password/abc', follow_redirects=True
    )
    assert b'That is an invalid or expired token' in response.data

    auth.login()
    response = client.get('/reset_password/eyJhbGciOiJIUzI1NiIsImlhdCI6MTUzNjkwODQ1OCwiZXhwIjoxNTM2OTEwMjU4fQ.eyJ1c2VyX2lkIjoxfQ.gb2ZkcoI5t2GmuYrrZQUD5_RqM1SiJ9g3S1QTlzD-KM')
    assert response.headers['Location'] == 'http://localhost/home'
    auth.logout()
    
    with app.app_context():
        user = User.query.first()
        token = user.get_reset_token()

    response = client.get(
        '/reset_password/'+token, follow_redirects=True
    )
    assert b'Reset Password' in response.data

    response = client.post(
        '/reset_password/'+token, data={'password': 'a12345',
                                        'confirm_password': 'a12345'}, 
                                        follow_redirects=True
    )
    assert b'Your password has been updated!' in response.data


@pytest.mark.parametrize(('route', 'message'), (
    ('/user_types', b"User Types"),
    ('/user_type/new', b"New User Type"),
    ('/user_type/1/update', b"Update User Type"),
    ('/users', b"All Users"),
))
def test_user_types(auth, client, route, message):
    response = client.get(route)
    assert response.headers['Location'] == 'http://localhost/login?next='+route.replace('/','%2F')

    response = auth.login(email='a12345@mycompany.com', password='test')
    assert response.headers['Location'] == 'http://localhost/home'

    response = client.get(route, follow_redirects=True)
    assert b"You don't have permission" in response.data

    auth.logout()
    auth.login()
    response = client.get(route, follow_redirects=True)
    assert message in response.data

def test_new_update_delete_user_type(auth, client):
    auth.login()
    response = client.post(
        '/user_type/new', data={'name': 'Losers'}
    )
    assert 'http://localhost/user_types' == response.headers['Location']
    response = client.get('/user_types', follow_redirects=True)
    assert b'Losers' in response.data
    
    response = client.post(
        '/user_type/2/update', data={'name': '1234567891011121314151617181920'}
    )
    assert b'Update User Type' in response.data

    response = client.post(
        '/user_type/2/update', data={'name': 'Flosers'}
    )
    assert 'http://localhost/user_types' == response.headers['Location']
    response = client.get('/user_types', follow_redirects=True)
    assert b'Flosers' in response.data

    response = client.post('/user_type/2/delete')
    assert 'http://localhost/user_types' == response.headers['Location']
    response = client.get('/user_types', follow_redirects=True)
    assert b'Flosers' not in response.data


def test_delete_user(client, auth):
    auth.login()
    response = client.get('/users', follow_redirects=True)
    assert b'a12345' in response.data
    response = client.post('/user/2/delete')
    assert 'http://localhost/users' == response.headers['Location']
    response = client.get('/users', follow_redirects=True)
    assert b'a12345' not in response.data


