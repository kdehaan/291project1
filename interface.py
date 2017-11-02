import time


class Interface:
    """
    Controller class to manage user input
    """
    userID = -1
    is_agent = False
    states = {}  # contains the state machine states
    state = 'l'  # init state machine on login menu

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
                print("Invalid Selection")
                time.sleep(0.4)

    def customer_menu(self):
        print('\n~~~~ Customer Menu ~~~~')
        print('Search for products: s')
        print('Place an order: p')
        print('List orders: l')
        print('Logout: o')
        selection = input('Please select an action: ')

        options = {'s': 'sp',
                   'p': 'po',
                   'l': 'lo',
                   'o': 'o'}
        try:
            return options[selection]
        except KeyError:
            return 'invalid'

    def search_products(self):
        print('~~~~ Product Search ~~~~')
        print('Multiple keywords separated by spaces may be entered')
        keywords = input('Enter keyword(s) to search for: ')
        for keyword in keywords:
            print(keyword)

        return 'cm'

    def place_order(self):
        print('~~~~ Place an Order ~~~~')
        # TODO

    def list_orders(self):
        print('~~~~ View Orders ~~~~')
        # TODO

    def agent_menu(self):
        print('\n~~~~ Agent Menu ~~~~')
        print('Set up a delivery: s')
        print('Update a delivery: u')
        print('Add to stock: a')
        print('Logout: o')
        selection = input('Please select an action: ')

        options = {'s': 'sd',
                   'u': 'ud',
                   'a': 'as',
                   'o': 'o'}
        try:
            return options[selection]
        except KeyError:
            return 'invalid'

    def set_delivery(self):
        print('~~~~ Create Delivery ~~~~')
        # TODO

    def update_delivery(self):
        print('~~~~ Update Delivery ~~~~')
        # TODO

    def add_stock(self):
        print('~~~~ Add to Stock ~~~~')
        # TODO

    def login_menu(self):
        print('\n~~~~ Login Menu ~~~~')
        print('Customer Login: c')
        print('Agent Login: a')
        print('Register: r')
        print('Exit Program: e')
        selection = input('Please select an action: ')

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
            time.sleep(0.4)
            state = input("Try again? [y/n]: ")
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
            time.sleep(0.4)
            state = input("Try again? [y/n]: ")
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
        time.sleep(0.4)
        return 'l'

    def register(self):
        print('~~~~ New Customer ~~~~')
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
        time.sleep(0.4)
        return 'l'

    def exit(self):
        print('-- Exiting Program --')
        return 'quit'


