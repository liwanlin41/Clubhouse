# Clubhouse

A website where Clubhouses in [The Clubhouse Network](https://theclubhousenetwork.org/) can track day-to-day check-ins of their members.

## HTML Language Instructions

Wrap all text to be displayed on the website like this.
```{{ _("display text")}}```
in the HTML file. Wanlin will then make the language translations work.

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
```source venv/bin/activate```
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
