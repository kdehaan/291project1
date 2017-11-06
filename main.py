import sqlite3
from sqlite3 import OperationalError, IntegrityError
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
            print("SQL Error: Command skipped: " + command)
        except IntegrityError:
            print(command + " Integrity Error")
            return
    conn.commit()


def setup():
    """
    Setup function
    :return:
    """

    sql.execute('''PRAGMA foreign_keys=ON;''')
    while True:
        file = input('File location of sql input code (leave empty for default, enter "c" when done): ')
        if not file:
            sql_from_file('./tables.sql')
            sql_from_file('./agents.sql')
            sql_from_file('./data.sql')
            break
        if file == 'c':
            break
        sql_from_file(file)

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
