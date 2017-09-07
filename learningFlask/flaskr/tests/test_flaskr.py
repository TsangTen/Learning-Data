import os
from flaskr import flaskr
import unittest
import tempfile


class FlaskrTestCase(unittest.TestCase):
    """
        The code in the setUp() method creates a new test client and initializes a new database.
        This function is called before each individual test function is run.
        To delete the database after the test,
        we close the file and remove it from the filesystem in the tearDown() method.
        Additionally during setup the TESTING config flag is activated.
        What it does is disable the error catching during request handling
        so that you get better error reports when performing test requests against the application.
    """

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        """Because SQLite3 is filesystem-based we can easily use the tempfile module 
        to create a temporary database and initialize it. 
        The mkstemp() function does two things for us: 
        it returns a low-level file handle and a random file name, 
        the latter we use as database name. 
        We just have to keep the db_fd around 
        so that we can use the os.close() function to close the file."""
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        """
        By using self.app.get we can send an HTTP GET request to the application with the given path.
        The return value will be a response_class object.
        We can now use the data attribute to inspect the return value (as string) from the application.
        In this case, we ensure that 'No entries here so far' is part of the output.
        """
        rv = self.app.get('/')
        assert b'No entries here so far.' in rv.data

    """Logging In and Out
    The majority of the functionality of our application 
    is only available for the administrative user, 
    so we need a way to log our test client in and out of the application. 
    To do this, we fire some requests to the login and logout pages 
    with the required form data (username and password). 
    And because the login and logout pages redirect, 
    we tell the client to follow_redirects."""

    def login(self, username, password):
        return self.app.post(
            '/login',
            data=dict(username=username, password=password),
            follow_redirects=True
        )

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    """Now we can easily test that logging in and out works 
    and that it fails with invalid credentials. """

    def test_login_logout(self):
        rv = self.login('admin', 'default')
        assert b'You were logged in' in rv.data
        rv = self.logout()
        assert b'You were logged out' in rv.data
        rv = self.login('adminx', 'default')
        assert b'Invalid username' in rv.data
        rv = self.login('admin', 'defaultx')
        assert b'Invalid password' in rv.data

    def test_message(self):
        """Here we check that HTML is allowed in the text but not in the title, which is the intended behavior."""
        self.login('admin', 'default')
        rv = self.app.post(
            '/add',
            data=dict(
                title='<Hello>',
                text='<strong>HTML</strong> allowed here'
            ),
            follow_redirects=True
        )
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data


if __name__ == '__main__':
    unittest.main()