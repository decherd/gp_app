from gp_app import create_app


def test_config():
	# Confirm default is not testing mode
    assert not create_app().testing
    # Pass TESTING and confirm is testing mode
    assert create_app({'TESTING': True}).testing

