import sqlite3
import pytest
from gp_app.models import User

# def test_get_close_db(app):
#     with app.app_context():
#         db = get_db()
#         assert db is get_db()

#     with pytest.raises(sqlite3.ProgrammingError) as e:
#         db.execute('SELECT 1')

#     assert 'closed' in str(e)

def test_model_user_repr(app):
	with app.app_context():
		user = User.query.first()
		assert str(user) == "User('test', 'test@mycompany.com')"


