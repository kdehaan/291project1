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
    selected_product = '-1'
    basket = []

    def __init__(self, conn, sql):
        self.conn = conn
        self.sql = sql
        self.states = {'l': self.login_menu,
                       'c': self.customer_login,
                       'a': self.agent_login,
                       'cm': self.customer_menu,
                       'sp': self.search_products,
                       'ps': self.product_submenu,
                       'po': self.place_order,
                       'lo': self.list_orders,
                       'am': self.agent_menu,
                       'sd': self.set_delivery,
                       'ud': self.update_delivery,
                       'as': self.add_stock,
                       'o': self.logout,
                       'r': self.register,
                       'e': self.exit
                       }

    def run(self):
        while True:
            selection = self.states[self.state]()
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

    def product_submenu(self):
        print('\n~~~~ Product Menu: ' + self.selected_product + ' ~~~~')
        return 'cm'

    def product_details(self, product_name):

        self.sql.execute('''select p.pid, p.unit
                            from products p
                            where p.name =:name''',
                         {'name': product_name})
        basic_details = self.sql.fetchall()[0]

        self.sql.execute('''select count(c.sid), min(c.uprice)
                            from products p, carries c
                            where p.name =:name
                            and c.pid = p.pid;''',
                         {'name': product_name})
        all_stores = self.sql.fetchall()[0]

        self.sql.execute('''select count(c.sid), min(c.uprice)
                            from products p, carries c
                            where p.name =:name
                            and c.pid = p.pid
                            and c.qty > 0;''',
                         {'name': product_name})
        in_stock = self.sql.fetchall()[0]

        self.sql.execute('''select count(o.oid)
                            from products p, olines ol, orders o
                            where p.name =:name
                            and p.pid = ol.pid
                            and ol.oid = o.oid
                            and o.odate < DATETIME("now", "-7 days");''',
                         {'name': product_name})
        recent_orders = self.sql.fetchall()[0]

        print('     PID: ' + basic_details[0])
        print('     Unit: ' + basic_details[1])
        if all_stores[0] == 0:
            print('     No Stores carry this item')
        else:
            print('     ' + str(all_stores[0]) + ' stores carry this, lowest price: ' + str(all_stores[1]))
            print('     ' + str(in_stock[0]) + ' stores have this in stock, lowest price: ' + str(in_stock[1]))
        print('     There have been ' + str(recent_orders[0]) + ' orders for this in the last 7 days')

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
                print('\n[' + str(index) + '] ' + row[0])
                self.product_details(row[0])
                index = index + 1
            sel = input('\nEnter a number to view details, or r to return: ')
            if sel == 'r':
                return 'cm'
            elif sel in {'1', '2', '3', '4', '5'}:
                self.selected_product = result[int(sel)-1][0]
                return 'ps'
            else:
                return 'error'

        else:
            print('\n-- No Results Found --')
            time.sleep(self.delay)

        return 'cm'

    def place_order(self):
        if not self.basket:
            print('Your basket is empty. Please choose at least one product before placing an order')
            return 'cm'
        else:
            print(' ')
            print('~~~~ Place an Order ~~~~')
            self.basket_check()
            totalCost = 0
            for item in self.basket:
                cost = item[2] * item[4]
                print(str(item[3]) + ' : (' + str(item[2]) + ' x ' + str(item[4]) +  '$)   :   ' + str(cost) + '$')
                totalCost += cost
            print('-----------------')
            print('Order total:     ' + str(totalCost) + '$')

            self.sql.execute('''select count(*)
                                from orders'''
                                )
            (oid,) = self.sql.fetchone()
            oid += 1
            self.sql.execute('''select address
                                from customers
                                where cid = :cid''',
                            {'cid': self.userID})
            (address,) = self.sql.fetchone()

            self.sql.execute('''insert into orders values
                              (:oid, :cname, DATETIME("now"), :address);''',
                             {'oid': oid, 'cname': self.userID, 'address': address})

            for item in self.basket:
                self.sql.execute('''update carries
                                    set qty = qty - :sold
                                    where pid = :pid  and sid = :sid;''',
                                 {'pid': item[0], 'sold': item[2], 'sid': item[1]})

                self.sql.execute('''insert into olines values
                                    (:oid, :sid, :pid, :qty, :uprice);''',
                                 {'oid': oid, 'sid': item[1], 'pid': item[0], 'qty': item[2], 'uprice': item[4]})
            self.conn.commit()
            self.basket = []
            print('Order placed. Your order id is ' + str(oid))

        return 'cm'

    def basket_check(self):
        for item in self.basket:
            if item[2] < 1:
                self.basket.remove(item)
            else:
                self.sql.execute('''select qty
                                    from carries c
                                    where c.sid = :isid and c.pid = :ipid''',
                                 {'isid': item[1], 'ipid': item[0]})
                (count,) = self.sql.fetchall()[0]
                if count < item [2]:
                    print('The store you are ordering ' + item[3] + ' from has ' + str(count) + ' in stock.')
                    answer = input('Would you like to remove this item (r), or change the quantity of this item (c)?').lower()
                    if answer == 'r':
                        self.basket.remove(item)
                    elif answer == 'c':
                        answer = input('Please enter the new amount you wish to order')
                        if self.hasint(answer):
                            if answer >= 0:
                                item[2] = int(answer)
                            print('Quantity updated!')
                        else:
                            print('Invalid input. Integer expected.')
                    else:
                        print('invalid input')
                    self.self.basket_check()

    def list_orders(self):
        print(' ')
        print('~~~~ View Orders ~~~~')
        self.sql.execute('''select o.oid, o.odate, sum(l.qty), sum(l.qty * l.uprice)
                            from olines l, orders o
                            where l.oid = o.oid''')
        ordr = self.sql.fetchall()
        done = False
        counter = -1
        answer = 'm'
        while not done:
            print('Entry        OrderID      Date Placed       Items Ordered     Total Cost')
            print('------------------------------------------------------------------------')
            if len(ordr) > 5:
                for i in range(0, 5):
                    if answer == 'm':
                        counter += 1
                    elif answer == 'l':
                        counter -= 1
                    print(str(counter) + '          ' + str(ordr[counter][0]) + '           ' + str(ordr[counter][1]) + '        '
                          + str(ordr[counter][2]) + '                      ' + str(ordr[counter][3]))
                if len(ordr) - 5 > counter > 3:
                    answer = input('Enter an entry number to see more information, "m" to see more, or "l" to see '
                                   'previous orders, or "q" to quit: ')
                    if self.hasint(answer):
                        pass
                    elif answer.lower() == 'l':
                        pass
                    elif answer.lower() == 'm':
                        pass
                    else:
                        answer = 'q'
                elif counter < len(ordr) - 5:
                    answer = input('Enter an entry number to see more information, "m" to see more, or "q" to quit: ')
                    if self.hasint(answer):
                        pass
                    elif answer.lower() == 'm':
                        pass
                    else:
                        answer = 'q'
                elif counter > 3:
                    answer = input('Enter an entry number to see more information, or "l" to see previous orders, or "q" to quit: ')
                    if self.hasint(answer):
                        pass
                    elif answer.lower() == 'l':
                        pass
                    else:
                        answer = 'q'
                if answer == 'q' or answer == 'Q':
                    return 'cm'
            else:
                for i in range(0, len(ordr)):
                    counter += 1
                    print(str(counter) + '              ' + str(ordr[counter][0]) + '      ' + str(ordr[counter][1]) + '    '
                          + str(ordr[counter][2]) + '                ' + str(ordr[counter][3]))
                answer = input('Enter an entry number to see more information, or "q" to quit: ')
                if self.hasint(answer):
                    pass
                else:
                    return 'cm'
            if self.hasint(answer):
                done = True
        if answer >= len(ordr) or answer < 0:
            return 'cm'
        else:
            self.sql.execute('''select d.trackingNo, d.pickUpTime, d.dropOffTime, o.address, l.sid, s.name, l.pid, p.name, l.qty, l.uprice
                                    from olines l, orders o, deliveries d, stores s, products p
                                    where l.oid = :oid and d.oid = l.oid and s.sid = l.sid and p.pid = l.pid;''',
                             {'oid': ordr[answer]})
            info = self.sql.fetchall()
            print('Tracking #: ' + str(info[0][0]) + '\n' + 'Pickup Time: ' + str(info[0][1]) + '\n' + 'Dropoff Time: ' + str(item[0][2]) + '\n' + 'Delivery Address: ' +
                  str(item[0][3]) + '\n' + 'ORDER CONTENTS:')
            totalprice = 0.00
            for i in info:
                print('Store ID: ' + str(i[4]) + '      Store Name: ' + str(i[5]) + '       Product ID: ' + str(i[6]) + '       Product Name: ' + str(i[7]) +
                      '     Quantity: ' + str(i[8]) + '     Unit Price: ' + str(i[9]) + '       Price: ' + str(i[8] * i[9]))
                totalprice += (i[8] * i[9])
            print('----------------------------------- Order Total: ' + str(totalprice))
            return 'cm'

    def hasint(answer):
        try:
            int(answer)
            return True
        except ValueError:
            return False

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
        self.basket = [['dai0', 0, 4, 'Milk, Whole, Jug', 6.00]]
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
        self.basket = []
        time.sleep(0.4)
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


