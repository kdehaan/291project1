import sqlite3
import tables


def create_connection():
    return sqlite3.connect('./data.db')


def setup():
    conn = create_connection()
    sql = conn.cursor();
    sql.execute('''PRAGMA foreign_keys=ON;''')
    tables.create_tables(conn, sql)

    conn.commit()


def main():
    setup()


if __name__ == '__main__':
    main()
