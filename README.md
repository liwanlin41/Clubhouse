# Clubhouse

A website where Clubhouses in [The Clubhouse Network](https://theclubhousenetwork.org/) can track day-to-day check-ins of their members.

## Flask Files

All the (important) flask files are now under the app directory. The main file to run is run_app.py (`export FLASK_APP=run_app.py`), with some auxiliary things in the main folder.

## HTML Language Instructions

Wrap all text to be displayed on the website like this.
`{{ _("display text")}}`
in the HTML file. Wanlin will then make the language translations work.

In python files, most translations seem to be needed in forms? See the forms.py file for an example, but in this case wrap the text as `_l("display text")`.

To run language compilation:

```
pybabel extract -F babel.cfg -k _l -o messages.pot --input-dirs=.
```
to get started, then
```
pybabel init -i messages.pot -d app/translations -l (insert language abbrev here)
```
which creates a language directory in the translations folder. This file (the .po one) can then be edited and translations inputted.
Finally to compile,
```
pybabel compile -d app/translations
```
and hopefully it works.

## Database Setup
This website uses a MySQL database, accessed through the Flask extension `flask-mysql`.

Once you have set up the MySQL instance database that you wish to use, you must set the following environment variables in the terminal where your app runs:

(note these are specific to the testing DB, and sensitive fields are being kept in a google doc not on GitHub)

```
export MYSQL_DATABASE_HOST=remotemysql.com
export MYSQL_DATABASE_USER=<yourUsername>
export MYSQL_DATABASE_PASSWORD=<yourPassword>
export MYSQL_DATABASE_DB=<yourDbName>
```

Alternatively, there is a bash script called `setup_sql` that contains these commands. Move it to the `bin` folder of the virtual environment and set the fields shown above; then running `setup_sql` inside the environment will run these commands.

Visit the `flask-mysql` [documentation](https://flask-mysql.readthedocs.io/en/latest/) for further reference if needed.

To obtain the tables needed for this app, if not done so already, create the tables specified in the schema file (this has been done already for the test database).

## Install and Run

These instructions require that Python 3 is already installed on the machine.

In a terminal window, navigate to the website directory and perform the following:

### Windows

Create a virtual environment and install dependencies:
```
py -3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Run the Flask app:
```
set FLASK_APP=app.py
flask run
```

You can now access your app at the displayed address.

If you quit the app, you can run it again with `flask run`.

### Other Operating Systems

Create a virtual environment and install dependencies:
```
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

To reactivate the virtual environment, either
```
venv/bin/activate
```
or
`source venv/bin/activate`
if the first one doesn't work.

Run the Flask app:
```
export FLASK_APP=app.py
flask run
```

You can now access your app at the displayed address.

If you quit the app, you can run it again with `flask run`.

### Debug Mode

To run in debug mode with auto-reloading on code changes, also set the environment variable `FLASK_ENV=development`.

## Reference
Check the Flask [Quickstart](https://flask.palletsprojects.com/en/1.1.x/quickstart/#) for further reference.
