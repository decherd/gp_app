import os
import tempfile

import pytest
from gp_app import create_app, db
from gp_app.models import User


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_path,
        'WTF_CSRF_ENABLED' : False,
    })

    with app.app_context():
        db.create_all()
        user = User(username='test',
                    email='test@mycompany.com',
                    password='$2b$12$XuPwoWD7h2SdH4O1QDEy6eM7VWm.N/TbKfo5AVTqS.PW4xpkkpKie'
                    )
        user2 = User(username='test2',
                    email='test2@mycompany.com',
                    password='$2b$12$XuPwoWD7h2SdH4O1QDEy6eM7VWm.N/TbKfo5AVTqS.PW4xpkkpKie'
                    )
        db.session.add(user)
        db.session.add(user2)
        db.session.commit()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email='test@mycompany.com', password='test', remember='False'):
        return self._client.post(
            '/login',
            data={'email': email, 'password': password, 'remember': remember}
        )

    def logout(self):
        return self._client.get('/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)