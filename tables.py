

def create_tables(conn, sql):
    sql.execute('''drop table if exists agents;''')
    sql.execute('''drop table if exists deliveries;''')
    sql.execute('''drop table if exists olines;''')
    sql.execute('''drop table if exists orders;''')
    sql.execute('''drop table if exists customers;''')
    sql.execute('''drop table if exists carries;''')
    sql.execute('''drop table if exists products;''')
    sql.execute('''drop table if exists categories;''')
    sql.execute('''drop table if exists stores;''')
    sql.execute('''
        create table agents (
            aid       int,
            name      text,
            pwd       text,
            primary key (aid));''')
    sql.execute('''
        create table stores (
            sid		int,
            name		text,
            phone		text,
            address	text,
            primary key (sid));''')
    sql.execute('''
        create table categories (
            cat           char(3),
            name          text,
            primary key (cat));''')
    sql.execute('''
        create table products (
            pid		char(6),
            name		text,
            unit		text,
            cat		char(3),
            primary key (pid),
            foreign key (cat) references categories);''')
    sql.execute('''
        create table carries (
            sid		int,
            pid		char(6),
            qty		int,
            uprice	real,
            primary key (sid,pid),
            foreign key (sid) references stores,
            foreign key (pid) references products);''')
    sql.execute('''
        create table customers (
            cid		text,
            name		text,
            address	text,
            pwd       text,
            primary key (cid));''')
    sql.execute('''
        create table orders (
            oid		int,
            cid		text,
            odate		date,
            address	text,
            primary key (oid),
            foreign key (cid) references customers);''')
    sql.execute('''
        create table olines (
            oid		int,
            sid		int,
            pid		char(6),
            qty		int,
            uprice	real,
            primary key (oid,sid,pid),
            foreign key (oid) references orders,
            foreign key (sid) references stores,
            foreign key (pid) references products);''')
    sql.execute('''
        create table deliveries (
            trackingNo	int,
            oid		int,
            pickUpTime	date,
            dropOffTime	date,
            primary key (trackingNo,oid),
            foreign key (oid) references orders);''')
    conn.commit()



