"""
Besides using the test client as shown above, there is also the test_request_context() method
that can be used in combination with the with statement to activate a request context temporarily.
With this you can access the request, g and session objects like in view functions.
"""

import flask

app = flask.Flask(__name__)

with app.test_request_context('/?name=Peter'):
    assert flask.request.path == '/'
    assert flask.request.args['name'] == 'Peter'

"""
If you want to test your application with different configurations 
and there does not seem to be a good way to do that, consider switching to application factories. 
"""

"""
Note however that if you are using a test request context, 
the before_request() and after_request() functions are not called automatically. 
However teardown_request() functions are indeed executed 
when the test request context leaves the with block. 
If you do want the before_request() functions to be called as well, 
you need to call preprocess_request() yourself.

app = flask.Flask(__name__)

with app.test_request_context('/?name=Peter'):
    app.preprocess_request()
    ....

This can be necessary to open database connections 
or something similar depending on how your application was designed.

--------------------------

If you want to call the after_request() functions you need to call into process_response() 
which however requires that you pass it a response object.

app = flask.Flask(__name__)

with app.test_request_context('/?name=Peter'):
    resp = Response('...')
    resp = app.process_response(resp)
    ...

This in general is less useful because at that point you can directly start using the test client.
"""

"""
Faking Resources and Context

New in version 0.10.

A very common pattern is to store user authorization information and database connections 
on the application context or the flask.g object. 
The general pattern for this is to put the object on there on first usage 
and then to remove it on a teardown. 
Imagine for instance this code to get the current user

def get_user():
    user = getattr(g, 'user', None)
    if user is None:
        user = fetch_current_user_from_database()
        g.user = user
    return user

----------

For a test it would be nice to override this user from the outside without having to change some code. 
This can be accomplished with hooking the flask.appcontext_pushed signal:


from contextlib import contextmanager
from flask import appcontext_pushed, g


@contextmanager
def user_set(app, user):
    def handler(sender, **kwargs):
        g.user = user
    with appcontext_pushed.connected_to(handler, app):
        yield
And then to use it:

from flask import json, jsonify

@app.route('/users/me')
def users_me():
    return jsonify(username=g.user.username)

with user_set(app, my_user):
    with app.test_client() as c:
        resp = c.get('/users/me')
        data = json.loads(resp.data)
        self.assert_equal(data['username'], my_user.username)
"""

"""
Keeping the Context Around

New in version 0.4.

Sometimes it is helpful to trigger a regular request 
but still keep the context around for a little longer 
so that additional introspection can happen. 
With Flask 0.4 this is possible by using the test_client() with a with block:

app = flask.Flask(__name__)

with app.test_client() as c:
    rv = c.get('/?tequila=42')
    assert request.args['tequila'] == '42'

If you were to use just the test_client() without the with block, 
the assert would fail with an error because request is no longer available 
(because you are trying to use it outside of the actual request).
"""

"""
Accessing and Modifying Sessions

New in version 0.8.

Sometimes it can be very helpful to access or modify the sessions from the test client. 
Generally there are two ways for this. 
If you just want to ensure that a session has certain keys set to certain values 
you can just keep the context around and access flask.session:

with app.test_client() as c:
    rv = c.get('/')
    assert flask.session['foo'] == 42

This however does not make it possible to also modify the session 
or to access the session before a request was fired. 
Starting with Flask 0.8 we provide a so called “session transaction” 
which simulates the appropriate calls to open a session in the context of the test client 
and to modify it. At the end of the transaction the session is stored. 
This works independently of the session backend used:

with app.test_client() as c:
    with c.session_transaction() as sess:
        sess['a_key'] = 'a value'
    # once this is reached the session was stored

Note that in this case you have to use the sess object instead of the flask.session proxy. 
The object however itself will provide the same interface.
"""




