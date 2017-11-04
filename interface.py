import time


class Interface:
    """
    Controller class to manage user input
    It's technically OO but not really, might as well be functional tbh
    """
    userID = -1
    is_agent = False
    states = {}  # contains the state machine states
    state = 'l'  # init state machine on login menu
    delay = 0.4

    def __init__(self, conn, sql):
        self.conn = conn
        self.sql = sql
        self.states = {'l': self.login_menu,
                       'c': self.customer_login,
                       'a': self.agent_login,
                       'cm': self.customer_menu,
                       'sp': self.search_products,
                       'po': self.place_order,
                       'lo': self.list_orders,
                       'am': self.agent_menu,
                       'sd': self.set_delivery,
                       'ud': self.update_delivery,
                       'as': self.add_stock,
                       'o': self.logout,
                       'r': self.register,
                       'e': self.exit}

    def run(self):
        while True:
            selection = self.states[self.state]().lower()
            if selection in self.states:
                self.state = selection
            elif selection == 'quit':
                return
            else:  # remains in same state if invalid input detected
                print("Invalid Entry")
                time.sleep(self.delay)

    def customer_menu(self):
        print('\n~~~~ Customer Menu ~~~~')
        print('Search for products: s')
        print('Place an order: p')
        print('List orders: l')
        print('Logout: o')
        selection = input('Please select an action: ').lower()

        options = {'s': 'sp',
                   'p': 'po',
                   'l': 'lo',
                   'o': 'o'}
        try:
            return options[selection]
        except KeyError:
            return 'invalid'

    def product_details(self, product_name):

        self.sql.execute('''select p.pid, p.unit
                            from products p
                            where p.name =:name''',
                         {'name': product_name})
        basic_details = self.sql.fetchall()

        self.sql.execute('''select count(c.sid), min(c.uprice)
                            from products p, carries c
                            where p.name =:name
                            and c.pid = p.pid;''',
                         {'name': product_name})
        all_stores = self.sql.fetchall()

        self.sql.execute('''select count(c.sid), min(c.uprice)
                            from products p, carries c
                            where p.name =:name
                            and c.pid = p.pid
                            and c.qty > 0;''',
                         {'name': product_name})
        in_stock = self.sql.fetchall()

        self.sql.execute('''select count(o.oid)
                            from products p, olines ol, orders o
                            where p.name =:name
                            and p.pid = ol.pid
                            and ol.oid = o.oid
                            and o.odate < DATETIME("now", "-7 days");''',
                         {'name': product_name})
        recent_orders = self.sql.fetchall()

        print(basic_details)
        print(all_stores)
        print(in_stock)
        print(recent_orders)

    def search_products(self):
        print('\n~~~~ Product Search ~~~~')
        print('Multiple keywords separated by spaces may be entered')
        keywords = input('Enter keyword(s) to search for: ').split()
        if not keywords:
            return 'error'
        for keyword in keywords:
            if not keyword.isalnum():
                return 'error'

        query = '''select p.name, p.pid
                   from products p
                   where p.name like '%%%s%%' ''' % (keywords[0])
        for keyword in keywords[1:]:
            query = query + '''or p.name like '%%%s%%' ''' % keyword
        query = query + '''order by ( 
                           case
                           when p.name like '%%%s%%' then 1
                           else 0
                           end ''' % (keywords[0])
        for keyword in keywords[1:]:
            query = query + '''+
                               case
                               when p.name like '%%%s%%' then 1
                               else 0
                               end ''' % keyword
        query = query + ''') desc limit 5'''
        self.sql.execute(query)
        result = self.sql.fetchall()
        if result:
            print('\n-- Results Found --')
            index = 1
            for row in result:
                print(str(index) + ' ' + ' ' + row[0])
                self.product_details(row[0])
                index = index + 1
            sel = input('\nEnter a number to view details, or r to return: ')
            if sel == 'r':
                return 'cm'
            else:
                # TODO
                return 'cm'

        else:
            print('\n-- No Results Found --')
            time.sleep(self.delay)

        return 'cm'

    def place_order(self):
        print('\n~~~~ Place an Order ~~~~')
        # TODO

    def list_orders(self):
        print('\n~~~~ View Orders ~~~~')
        # TODO

    def agent_menu(self):
        print('\n~~~~ Agent Menu ~~~~')
        print('Set up a delivery: s')
        print('Update a delivery: u')
        print('Add to stock: a')
        print('Logout: o')
        selection = input('Please select an action: ').lower()

        options = {'s': 'sd',
                   'u': 'ud',
                   'a': 'as',
                   'o': 'o'}
        try:
            return options[selection]
        except KeyError:
            return 'invalid'

    def set_delivery(self):
        print('\n~~~~ Create Delivery ~~~~')
        # TODO

    def update_delivery(self):
        print('\n~~~~ Update Delivery ~~~~')
        # TODO

    def add_stock(self):
        print('\n~~~~ Add to Stock ~~~~')
        # TODO

    def login_menu(self):
        print('\n~~~~ Login Menu ~~~~')
        print('Customer Login: c')
        print('Agent Login: a')
        print('Register: r')
        print('Exit Program: e')
        selection = input('Please select an action: ').lower()

        options = {'c': 'c',
                   'a': 'a',
                   'r': 'r',
                   'e': 'e'}
        try:
            return options[selection]
        except KeyError:
            return 'invalid'

    def customer_login(self):
        print('\n~~~~ Customer Login ~~~~~')
        cid = input('CID: ')
        password = input('Password: ')
        self.sql.execute('''select c.name, c.cid
                            from customers c
                            where c.cid=:cid
                            and c.pwd=:pwd''',
                         {'cid': cid, 'pwd': password})
        response = self.sql.fetchall()
        if not response:
            print("Invalid ID or Password")
            time.sleep(self.delay)
            state = input("Try again? [y/n]: ").lower()
            if state == 'n':
                return 'l'
            else:
                return 'c'
        else:
            print(response[0])
            self.userID = cid
            return 'cm'

    def agent_login(self):
        print('\n~~~~ Agent Login ~~~~')
        aid = input('AID: ')
        password = input('Password: ')
        self.sql.execute('''select a.name, a.aid
                            from agents a
                            where a.aid=:aid
                            and a.pwd=:pwd''',
                         {'aid': aid, 'pwd': password})

        response = self.sql.fetchall()
        if not response:
            print("Invalid ID or Password")
            time.sleep(self.delay)
            state = input("Try again? [y/n]: ").lower()
            if state == 'n':
                return 'l'
            else:
                return 'a'
        else:
            print(response[0])
            self.userID = aid
            self.is_agent = True
            return 'am'

    def logout(self):
        self.is_agent = False
        print("-- Logged out of " + self.userID + ' --')
        self.userID = -1
        time.sleep(self.delay)
        return 'l'

    def register(self):
        print('\n~~~~ New Customer ~~~~')
        cid = input('CID: ')
        self.sql.execute('''select c.cid
                            from customers c
                            where c.cid=:cid''',
                         {'cid': cid})
        response = self.sql.fetchall()
        if response:
            print("Error: CID already exists")
            return 'r'
        name = input('Name: ')
        address = input('Address: ')
        password = input('Password: ')
        self.sql.execute('''insert into customers values
                            (:cid, :name, :address, :password);''',
                         {'cid': cid, 'name': name, 'address': address, 'password': password})
        self.conn.commit()
        print("\n-- User Successfully Registered --")
        time.sleep(self.delay)
        return 'l'

    def exit(self):
        print('-- Exiting Program --')
        return 'quit'


