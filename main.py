import sqlite3
from sqlite3 import OperationalError
import interface

conn = sqlite3.connect('./data.db')
sql = conn.cursor()
i = interface.Interface(conn, sql)


def sql_from_file(filename):
    """
    Adapted from https://stackoverflow.com/a/19473206
    Runs sql queries from a .sql or .txt file
    :param filename:
    :return:
    """
    f = open(filename, 'r')
    sql_file = f.read()
    f.close()
    commands = sql_file.split(';')
    for command in commands:
        try:
            sql.execute(command)
        except OperationalError:
            print("Command skipped")
    conn.commit()


def setup():
    """
    Setup function
    :return:
    """
    sql.execute('''PRAGMA foreign_keys=ON;''')
    sql_from_file('./tables.sql')
    sql_from_file('./agents.sql')

    conn.commit()


def main():
    """
    Main function
    :return:
    """
    setup()
    i.run()


if __name__ == '__main__':
    main()
