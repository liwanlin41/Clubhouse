# Clubhouse

A website where Clubhouses in [The Clubhouse Network](https://theclubhousenetwork.org/) can track day-to-day check-ins of their members.

## Making Changes and Deploying to AWS Server

For ease of deployment, install the Elastic Beanstalk Command Line Interface (https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html) inside a virtual environment.
Prepare AWS access key credentials (found under My Security Credentials on the AWS console).
You will probably be prompted for these the first time you create/link to an application.
Only two access keys can exist at any given time, so the old keys can be deleted and replaced with new ones. Then this entire process would need to be repeated. (Note that this is untested speculation and there might be further complications.)

### Linking

To create a **new** application:

1. Create a new key pair in the EC2 key pair console on AWS. Move this to wherever your local .ssh directory is.
2. Locally run `eb init` (with the --interactive flag if no prompts show up) and select the appropriate options. Code commit is unnecessary. Make sure to select the key pair chosen above for ssh.
3. Run eb create to create a new environment. Run eb deploy to actually deploy the code in the git repo.
4. Go to the AWS console for this environment and modify the following in software under the configuration tab:
    - set the static files to application/static/ in the box to the right of /static/
    - set MYSQL_DATABASE_DB, MYSQL_DATABASE_HOST, MYSQL_DATABASE_PASSWORD, MYSQL_DATABASE_USER as environment properties with the appropriate values. This is the equivalent of any `export VARIABLE=value` commands in the local virtual environment.


To link to an existing application, just do the first two steps above.

### Making Updates

Elastic Beanstalk is linked to git status. Inside the git repo, commit and push any changes that were made. Activate the virtual environment (`source venv/bin/activate`) and run `eb deploy`. If the Elastic Beanstalk setup was successful, this should automatically push the local changes to the server and update the live website.

### SSH

Assuming the key pair generated during setup is already in your local .ssh directory, `eb ssh` should directly ssh into this Elastic Beanstalk instance.

One issue that comes up sometimes is a Permission denied: (publickey) error. I don't actually know how to fix this, but my guess is this is an issue that cropped up as we continually messed around with all of the setup and likely broke some things while trying to figure everything out.
Re-deploying in a completely new application/environment for actual site use should fix the problem.

## Local Testing and Component Documentation

### Flask Files

All the (important) flask files are now under the app directory. The main file to run is application.py (`export FLASK_APP=application.py`), with some auxiliary things in the main folder.

### HTML Language Instructions

Wrap all text to be displayed on the website like this.
`{{ _("display text")}}`
in the HTML file. Flask-Babel looks for this to make the language translations work.

In python files, most translations seem to be needed in forms? See the forms.py file for an example, but in this case wrap the text as `_l("display text")`.

To run language compilation:

```
pybabel extract -F babel.cfg -k _l -o messages.pot --input-dirs=.
```
to get started, then **for a new language**
```
pybabel init -i messages.pot -d app/translations -l (insert language abbrev here)
```
which **creates** a language directory in the translations folder. To update the translation file **for a preexisting language**, run
```
pybabel update -i messages.pot -d app/translations -l (insert language abbrev here)
```
This file (the .po one) can then be edited and translations inputted.
Finally to compile,
```
pybabel compile -d app/translations
```
and hopefully it works.

In addition, when adding a new language please also add the abbreviation for that language in the `config.py LANGUAGES` list.

Note that none of this has been tested for the live server.

### Database Setup
This website uses a MySQL database, accessed through the Flask extension `flask-mysql`.

Once you have set up the MySQL instance database that you wish to use, you must set the following environment variables in the terminal where your app runs:

(note these are specific to the testing DB, and sensitive fields are being kept in a google doc not on GitHub)

```
export MYSQL_DATABASE_HOST=remotemysql.com
export MYSQL_DATABASE_USER=<yourUsername>
export MYSQL_DATABASE_PASSWORD=<yourPassword>
export MYSQL_DATABASE_DB=<yourDbName>
```

Alternatively, there is a bash script called `setup_sql` that contains these commands. Move it to the `bin` folder of the virtual environment and set the fields shown above; then running `setup_sql` or `source setup_sql` inside the environment will run these commands.

Visit the `flask-mysql` [documentation](https://flask-mysql.readthedocs.io/en/latest/) for further reference if needed.

To obtain the tables needed for this app, if not done so already, create the tables specified in the schema file (this has been done already for the test database).

### Install and Run

These instructions require that Python 3 is already installed on the machine.

In a terminal window, navigate to the website directory and perform the following:

#### Windows

Create a virtual environment and install dependencies:
```
py -3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Run the Flask app:
```
set FLASK_APP=application.py
flask run
```

You can now access your app at the displayed address.

If you quit the app, you can run it again with `flask run`.

#### Other Operating Systems

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
export FLASK_APP=application.py
flask run
```

You can now access your app at the displayed address.

If you quit the app, you can run it again with `flask run`.

#### Debug Mode

To run in debug mode with auto-reloading on code changes, also set the environment variable `FLASK_ENV=development`.

### Reference
Check the Flask [Quickstart](https://flask.palletsprojects.com/en/1.1.x/quickstart/#) for further reference.

## Bug Reports

Website error logs can be found by selecting the application environment on the AWS console and going to the logs tab.

- Off a server restart, the first login redirect takes forever. Refreshing the site fixes the problem and subsequent logins are fine, and this problem has not been duplicated on other computers. (This was on chrome with Ubuntu 18.04.)

- Database connections: the original problem was `pymysql.err.interfaceerror: (0, '')`. A patch was slapped over this by creating a new database connection for every database request, but now there are errors of too many database connections. A proposed fix was to ssh into the eb istance and set wait_timeout to a relatively small number in `/etc/my.cnf`. The units for this field are in seconds, and it defaults to 28800.
