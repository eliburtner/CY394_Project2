import flask
import mysql.connector
import click
import os
from flask import current_app
from flask import g

def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "mysql"),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", "password"),
            database=os.environ.get("MYSQL_DB", "phase2-mysql-database")
        )
        print("Connected db:")
    
    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Clear existing data and create new tables."""
    db = get_db()
    cursor = db.cursor()

    with current_app.open_resource("schema.sql") as f:
        sqlscript = f.read().decode("utf8")
        print(f"executing {sqlscript}")
        result = cursor.execute(sqlscript, multi=True)
        #pdb.set_trace()
        print("completed script")
        for r in result:
            print(r)
    
    print("Check:")
    checkresults = cursor.execute('SHOW TABLES;')
    for r in cursor.fetchall():
        print(r)

    

@click.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
