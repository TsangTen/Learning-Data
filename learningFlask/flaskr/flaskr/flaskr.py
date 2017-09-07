# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, _app_ctx_stack


app = Flask(__name__)  # create our little application :)
app.config.from_object(__name__)  # load config from this file , flaskr.py
"""
You can use the from_object() method on the config object 
and provide it with an import name of a module. 
Flask will then initialize the variable from that module. 
Note that in all cases, 
only variable names that are uppercase are considered.
"""
# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',  # The SECRET_KEY is needed to keep the client-side sessions secure.
    USERNAME='admin',
    PASSWORD='default'
))  # The Config object works similarly to a dictionary, so it can be updated with new values.
app.config.from_envvar('FLASKR_SETTING', silent=True)
"""
Usually, it is a good idea to load a separate, 
environment-specific configuration file. 
Flask allows you to import multiple configurations 
and it will use the setting defined in the last import. 
This enables robust configuration setups. 
from_envvar() can help achieve this.
Simply define the environment variable FLASKR_SETTINGS 
that points to a config file to be loaded. 
The silent switch just tells Flask to not complain 
if no such environment key is set.
"""


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv
"""
You can create a simple database connection through SQLite 
and then tell it to use the sqlite3.Row object to represent rows. 
This allows the rows to be treated as if they were dictionaries 
instead of tuples.
"""


"""
Flask provides two contexts: 
the application context and the request context. 
For the time being, 
all you have to know is that there are special variables 
that use these. 
For instance, 
the request variable is the request object 
associated with the current request, 
whereas g is a general purpose variable 
associated with the current application context. 
"""
# For the time being,
# all you have to know is that you can store information safely on the g object.


def get_db():
    """
    Opens a new database connection if there is none yet for
    the current application context.
    """
    # top = _app_ctx_stack.top
    # if not hasattr(top, 'sqlite_db'):
    #     top.sqlite_db = connect_db()
    # return top.sqlite_db
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        """
        The open_resource() method of the application object is a convenient helper function 
        that will open a resource that the application provides. 
        This function opens a file from the resource location (the flaskr/flaskr folder) 
        and allows you to read from it. 
        It is used in this example to execute a script on the database connection.
        """
        db.cursor().executescript(f.read())
    db.commit()
    """
    The connection object provided by SQLite can give you a cursor object. 
    On that cursor, there is a method to execute a complete script. 
    Finally, you only have to commit the changes. 
    SQLite3 and other transactional databases will not commit unless you explicitly tell it to.
    """


"""
The app.cli.command() decorator registers a new command with the flask script. 
When the command executes, 
Flask will automatically create an application context 
which is bound to the right application. 
Within the function, 
you can then access flask.g and other things as you might expect. 
When the script ends, 
the application context tears down and the database connection is released.
"""


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


"""
 Flask provides us with the teardown_appcontext() decorator. 
 It's executed every time the application context tears down
"""


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    # top = _app_ctx_stack.top
    # if hasattr(top, 'sqlite_db'):
    #     top.sqlite_db.close()
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
"""
Functions marked with teardown_appcontext() are called every time the app context tears down.
What does this mean?
Essentially, the app context is created before the request comes in 
and is destroyed (torn down) whenever the request finishes.
A teardown can happen because of two reasons:
either everything went well (the error parameter will be None) or an exception happened,
in which case the error is passed to the teardown function.
"""


@app.route('/')
def show_entries():  # This view shows all the entries stored in the database.
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)
"""
The view function will pass the entries to the show_entries.html template 
and return the rendered one
"""


@app.route('/add', methods=['POST'])
def add_entry():  # This view lets the user add new entries if they are logged in.
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))
"""
This only responds to POST requests; 
the actual form is shown on the show_entries page. 
If everything worked out well, 
it will flash() an information message to the next request 
and redirect back to the show_entries page.
"""


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login checks the username and password against
    the ones from the configuration and sets the logged_in key for the session.
    If the user logged in successfully,
    that key is set to True, and the user is redirected back to the show_entries page.
    In addition, a message is flashed that informs
    the user that he or she was logged in successfully.
    If an error occurred, the template is notified about that,
    and the user is asked again.
    """
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = ' Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """
    The logout function, on the other hand, removes that key from the session again.
    There is a neat trick here:
    if you use the pop() method of the dict and pass a second parameter to it (the default),
    the method will delete the key from the dictionary if present
    or do nothing when that key is not in there.
    This is helpful because now it is not necessary to check if the user was logged in.
    """
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    init_db()
    app.run()


