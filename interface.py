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
    selected_product_ID = '-1'
    basket = []
    page = 0
    search_result = []

    def __init__(self, conn, sql):
        self.conn = conn
        self.sql = sql
        self.states = {'l': self.login_menu,
                       'c': self.customer_login,
                       'a': self.agent_login,
                       'cm': self.customer_menu,
                       'sp': self.search_products,
                       'sr': self.search_results,
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

    def basket_add(self, basket_item):
        duplicate = False
        for item in self.basket:
            if item[0] == basket_item[0]:
                if item[1] == basket_item[1]:
                    item[2] += basket_item[2]
                    duplicate = True
        if not duplicate:
            self.basket.append(basket_item)

    def product_submenu(self):
        options = {'s': 'sr', 'm': 'cm'}
        self.sql.execute('''select p.name, p.pid, c.name, p.unit
                            from products p, categories c
                            where p.pid=:pid
                            and p.cat = c.cat''',
                        {'pid': self.selected_product_ID})
        product = self.sql.fetchall()[0]

        print('\n~~~~ Product Menu: ' + product[0] + ' ~~~~')
        print('PID: ' + product[1])
        print('Unit: ' + product[3])
        print('Category: ' + product[2])

        self.sql.execute('''select count(c.sid)
                            from products p, carries c
                            where p.pid =:pid
                            and c.pid = p.pid;''',
                         {'pid': product[1]})
        num_stores = self.sql.fetchone()[0]
        if num_stores == 0:
            print('-- No stores carry this product --')
            sel = input('\nEnter s to return to search results, or m to return to the customer menu: ')
            options = {'s': 'sr', 'm': 'cm'}
            return options[sel]
        elif num_stores == 1:
            print('One store carries this product:')
            self.sql.execute('''select s.name, c.uprice, c.qty, s.sid
                                from products p, carries c, stores s
                                where p.pid =:pid
                                and c.pid = p.pid
                                and s.sid = c.sid;''',
                             {'pid': product[1]})
            store = self.sql.fetchall()[0]
            self.sql.execute('''select count(o.oid)
                                from products p, olines ol, orders o
                                where p.pid=:pid
                                and ol.oid = o.oid
                                and o.odate < DATETIME("now", "-7 days")
                                and ol.sid =:sid''',
                             {'pid': product[1], 'sid': store[3]})
            recent_orders = self.sql.fetchall()

            print('\n[1] Store: ' + store[0])
            print('     Price: ' + str(store[1]))
            print('     Quantity: ' + str(store[2]))
            if not recent_orders:
                print('     Recent orders: 0')
            else:
                print('     Recent orders: ' + str(recent_orders[0][0]))

            sel = input('\nEnter 1 to add this product to your basket, s to return to search '
                        'results, or m to return to the customer menu: ')
            if sel == '1':
                print('-- 1 unit of ' + product[0] + ' from store ' + store[0] + ' added to basket --')
                sel = input('\nEnter c to confirm, r to remove, or an integer value to change the quantity desired: ')
                quantity = 1
                if self.hasint(sel):
                    quantity = int(sel)
                    print('-- Quantity updated to ' + sel + ' --')
                if sel == 'c' or self.hasint(sel):
                    basket_item = [product[1], store[3], quantity, product[0], store[1]]
                    self.basket_add(basket_item)
                else:
                    return 'error'
            elif sel in options:
                return options[sel]

        else:
            print('The following ' + str(num_stores) + ' stores carry this product:')
            self.sql.execute('''select s.name, c.uprice, c.qty, s.sid
                                from products p, carries c, stores s
                                where p.pid =:pid
                                and c.pid = p.pid
                                and s.sid = c.sid
                                and c.qty > 0
                                order by c.uprice asc;''',
                             {'pid': product[1]})
            in_stock = self.sql.fetchall()
            self.sql.execute('''select s.name, c.uprice, c.qty, s.sid
                                            from products p, carries c, stores s
                                            where p.pid =:pid
                                            and c.pid = p.pid
                                            and s.sid = c.sid
                                            and c.qty = 0
                                            order by c.uprice asc;''',
                             {'pid': product[1]})
            no_stock = self.sql.fetchall()

            either_stock = in_stock + no_stock
            index = 1
            for store in either_stock:
                self.sql.execute('''select count(o.oid)
                                                from products p, olines ol, orders o
                                                where p.pid=:pid
                                                and ol.oid = o.oid
                                                and o.odate < DATETIME("now", "-7 days")
                                                and ol.sid =:sid''',
                                 {'pid': product[1], 'sid': store[3]})
                recent_orders = self.sql.fetchall()
                print('\n[' + str(index) + '] Store: ' + store[0])
                print('     Price: ' + str(store[1]))
                print('     Quantity: ' + str(store[2]))
                if not recent_orders:
                    print('     Recent orders: 0')
                else:
                    print('     Recent orders: ' + str(recent_orders[0][0]))
                index = index + 1
            sel = input('\nEnter a number to add the product from that store to your basket, s to return to search '
                        'results, or m to return to the customer menu: ')

            basket_options = range(len(either_stock))
            basket_options = ['{:d}'.format(x+1) for x in basket_options]

            if sel in basket_options:
                store_entry = either_stock[int(sel)-1]
                print('-- 1 unit of ' + product[0] + ' from store ' + store_entry[0] + ' added to basket --')
                sel = input('\nEnter c to confirm, r to remove, or an integer value to change the quantity desired: ')
                quantity = 1
                if self.hasint(sel):
                    quantity = int(sel)
                    print('-- Quantity updated to ' + sel + ' --')
                if sel == 'c' or self.hasint(sel):
                    basket_item = [product[1], store_entry[3], quantity, product[0], store_entry[1]]
                    self.basket_add(basket_item)
                else:
                    return 'error'
            elif sel in options:
                return options[sel]
            else:
                return 'error'

        sel = input('Enter s to return to search results, or m to return to the customer menu: ')

        return options[sel]

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

    def search_results(self):
        print('\n-- Results Found --')
        result = self.search_result
        index = 1
        for row in result[self.page * 5:]:
            print('\n[' + str(index) + '] ' + row[0])
            self.product_details(row[0])
            index = index + 1
            if index > 5:
                break
        if len(result) > 5:
            print('\nThere are multiple pages of results, enter f or b to go forward or backwards in pages')
            print('You are currently on page ' + str(self.page+1))
        sel = input('\nEnter a number to view details, or r to return: ')
        if sel == 'r':
            return 'cm'
        elif sel == 'f':
            self.page = self.page + 1
            return 'sr'
        elif sel == 'b':
            self.page = self.page - 1
            if self.page < 0:
                self.page = 0
            return 'sr'
        elif sel in {'1', '2', '3', '4', '5'}:
            self.selected_product_ID = result[(self.page * 5) + int(sel) - 1][1]
            return 'ps'
        else:
            return 'error'

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
        query = query + ''') desc'''
        self.sql.execute(query)
        result = self.sql.fetchall()

        if result:
            self.page = 0
            self.search_result = result
            return 'sr'

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
                if count < item[2]:
                    print('The store you are ordering ' + item[3] + ' from has ' + str(count) + ' in stock.')
                    answer = input('Would you like to remove this item (r), or change the quantity of this item (c)?').lower()
                    if answer == 'r':
                        self.basket.remove(item)
                    elif answer == 'c':
                        answer = input('Please enter the new amount you wish to order')
                        if self.hasint(answer):
                            answer = int(answer)
                            if answer >= 0:
                                item[2] = int(answer)
                                print('Quantity updated!')
                        else:
                            print('Invalid input. Integer expected.')
                    else:
                        print('invalid input')
                    self.basket_check()

    def list_orders(self):
        print(' ')
        print('~~~~ View Orders ~~~~')
        self.sql.execute('''select o.oid, o.odate, sum(l.qty), sum(l.qty * l.uprice), count(*)
                            from olines l, orders o
                            where l.oid = o.oid and o.cid = :cid
                            group by o.oid;''',
                         {'cid': self.userID})
        ordr = self.sql.fetchall()
        if not ordr:
            print('You have no orders.')
            return 'cm'
        done = False
        counter = -1
        answer = 'm'
        while not done:
            print('Entry        OrderID      Date Placed       Items Ordered     Total Cost')
            print('------------------------------------------------------------------------')
            if len(ordr) > 4:
                for i in range(0, 5):
                    if answer == 'm':
                        counter += 1
                    elif answer == 'l':
                        counter -= 1
                    print(str(counter) + '          ' + str(ordr[counter][0]) + '           ' + str(ordr[counter][1]) + '        '
                          + str(ordr[counter][2]) + '                      ' + str(ordr[counter][3]))
                if len(ordr) - 5 > counter and counter > 5:
                    answer = input('Enter an entry number to see more information, "m" to see more, or "l" to see '
                                   'previous orders, or "q" to quit: ')
                    if self.hasint(answer):
                        answer = int(answer)
                    elif answer.lower() == 'l':
                        pass
                    elif answer.lower() == 'm':
                        pass
                    else:
                        answer = 'q'
                elif counter < len(ordr) - 5:
                    answer = input('Enter an entry number to see more information, "m" to see more, or "q" to quit: ')
                    if self.hasint(answer):
                        answer = int(answer)
                    elif answer.lower() == 'm':
                        pass
                    else:
                        answer = 'q'
                elif counter > 3:
                    answer = input('Enter an entry number to see more information, or "l" to see previous orders, or "q" to quit: ')
                    if self.hasint(answer):
                        answer = int(answer)
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
        answer = int(answer)
        if answer >= len(ordr) or answer < 0:
            return 'cm'
        else:
            self.sql.execute('''select d.trackingNo, d.pickUpTime, d.dropOffTime, o.address, l.sid, s.name, l.pid, p.name, l.qty, l.uprice
                                    from olines l, orders o, deliveries d, stores s, products p
                                    where l.oid = :oid and o.oid = l.oid and d.oid = l.oid and s.sid = l.sid and p.pid = l.pid''',
                             {'oid': ordr[answer][0]})
            info = self.sql.fetchall()
            try:
                print('Tracking #: ' + str(info[0][0]) + '\n' + 'Pickup Time: ' + str(info[0][1]) + '\n' + 'Dropoff Time: ' + str(info[0][2]) + '\n' + 'Delivery Address: ' +
                      str(info[0][3]) + '\n' + 'ORDER CONTENTS:')
                totalprice = 0.00
                for i in info:
                    print('Store ID: ' + str(i[4]) + '      Store Name: ' + str(i[5]) + '       Product ID: ' + str(i[6]) + '       Product Name: ' + str(i[7]) +
                          '     Quantity: ' + str(i[8]) + '     Unit Price: ' + "{0:.2f}".format(round(i[9])) + '$       Price: ' + "{0:.2f}".format(round(i[8] * i[9],2)) + '$')
                    totalprice += (i[8] * i[9])
                print('----------------------------------- Order Total: ' + "{0:.2f}".format(round(totalprice)) + '$')
                return 'cm'
            except exception:
                self.sql.execute('''select o.address, l.sid, s.name, l.pid, p.name, l.qty, l.uprice
                                        from olines l, orders o, deliveries d, stores s, products p
                                        where l.oid = :oid and o.oid = l.oid and s.sid = l.sid and p.pid = l.pid''',
                                 {'oid': ordr[answer][0]})
                info = self.sql.fetchall()
                print('This order is not part of a delivery' + '\n' + 'Delivery Address: ' +
                      str(info[0][0]) + '\n' + 'ORDER CONTENTS:')
                totalprice = 0.00
                for i in info:
                    print('Store ID: ' + str(i[1]) + '      Store Name: ' + str(i[2]) + '       Product ID: ' + str(i[3]) + '       Product Name: ' + str(i[4]) +
                          '     Quantity: ' + str(i[5]) + '     Unit Price: ' + "{0:.2f}".format(round(i[6])) + '$       Price: ' + "{0:.2f}".format(round(i[5] * i[6],2)) + '$')
                    totalprice += (i[5] * i[6])
                print('----------------------------------- Order Total: ' + "{0:.2f}".format(round(totalprice)) + '$')
                return 'cm'

    def hasint(self, answer):
        try:
            int(answer)
            if int(answer) < 0:
                return False
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
        done = False
        self.sql.execute('''select count(*)
                            from deliveries
                            group by trackingNo''')
        tracknum = self.sql.fetchall()[0][0] + 1
        while not done:
            found = False
            while not found:
                ordernum = input('Please enter an order that you would like to add to the delivery, or press "q" to quit: ')
                if self.hasint(ordernum):
                    ordernum = int(ordernum)
                    self.sql.execute('''select o.oid
                                        from orders o, deliveries d
                                        where o.oid = :oid and o.oid not in (select oid
                                                                             from deliveries)''',
                                     {'oid': ordernum})
                    reqdorder = self.sql.fetchall()
                    if not reqdorder:
                        print('That order does not exist, or is already on a delivery.')
                    else:
                        dropoff = ''
                        dropoff = input('Please enter a pickup time for the order: ')
                        if dropoff == '':
                            self.sql.execute('''insert into deliveries values
                                                (:trackingNo, :oid, Null, Null);''',
                                             {'trackingNo': tracknum, 'oid': reqdorder[0][0]})
                            self.conn.commit()
                        else:
                            self.sql.execute('''insert into deliveries values
                                                (:trackingNo, :oid, :pickup, Null);''',
                                             {'trackingNo': tracknum, 'oid': reqdorder[0][0], 'pickup': dropoff})
                            self.conn.commit()
                        print('Success! Order ' + str(reqdorder[0][0]) + ' has been added to delivery ' + str(tracknum))
                elif ordernum == 'q':
                    return 'am'

                else:
                    print('Please enter an integer')

    def update_delivery(self):
        print('\n~~~~ Update Delivery ~~~~')
        done = False
        while not done:
            ordernum = input('Please enter the tracking number of the delivery you wish to modify: ')
            if self.hasint(ordernum):
                ordernum = int(ordernum)
                self.sql.execute('''select trackingNo, oid, pickUpTime, dropOffTime, count(*)
                                    from deliveries
                                    where trackingNo = :track
                                    group by oid''',
                                 {'track': trackingNo})
                trackempty = self.sql.fetchall()
                if not trackempty:
                    print('That tracking number does not exist')
                else:
                    print('TrackingNo: ' + str(trackempty[0][0]) + '          Pickup Time: ' + str(trackempty[0][2]) +
                          '          Dropoff Time: ' + str(trackempty[0][3]))
                    print('Orders:')
                    for i in trackempty:
                        print('Order ' + str(i[1]))
                    choice = input('Would you like to pick up and order (p), or remove an order (r): ')
                    if choice == 'r':
                        ordernum = input('Which order would you like to remove: ')
                        if self.hasint(ordernum):
                            int(ordernum)
                            self.sql.execute('''select oid
                                                from deliveries
                                                where oid = :oid''',
                                             {'oid': ordernum})
                            order = self.sql.fetchall()
                            if self.
            else:
                print('That is not a valid delivery number')

    def add_stock(self):
        print('\n~~~~ Add to Stock ~~~~')
        done = False
        while not done:
            pid = input('Please enter the id of the product you wish to modify, or press q to quit: ')
            if pid == 'q':
                return 'am'
            sid = input('Please enter the id of the store you wish to modify, or press q to quit: ')
            if sid == 'q':
                return 'am'
            if self.hasint(sid):
                self.sql.execute('''select sid
                                    from carries
                                    where :sid = sid''',
                                 {'sid': sid})
                sidlist = self.sql.fetchall()
                self.sql.execute('''select pid
                                    from products
                                    where :pid = pid''',
                                 {'pid': pid})
                pidlist = self.sql.fetchall()
                if not pidlist or not sidlist:
                    print('That store or product does not exist. Please try again')
                else:
                    change = input('Would you like to change the stock (s) or the price (p)? ')
                    if change == 's':
                        amount = int(input('How many of this product would you like to add to the store? '))
                        self.sql.execute('''select *
                                            from carries
                                            where :sid = sid and :pid = pid''',
                                         {'sid': sid, 'pid': pid})
                        hasit = self.sql.fetchall()
                        if not hasit:
                            price = float(input('What price would you like to set for this product? '))
                            self.sql.execute('''insert into carries values
                                                (:sid, :pid, :amount, :price)''',
                                             {'sid': sid, 'pid': pid, 'amount': amount, 'price': price})
                            self.conn.commit()
                        else:
                            self.sql.execute('''update carries
                                                set qty = qty + :amount
                                                where :sid = sid and :pid = pid''',
                                             {'sid': sid, 'pid': pid, 'amount': amount})
                            self.conn.commit()
                    elif change == 'p':
                        self.sql.execute('''select *
                                            from carries
                                            where :sid = sid and :pid = pid''',
                                         {'sid': sid, 'pid': pid})
                        hasit = self.sql.fetchall()
                        if not hasit:
                            print('That product does not exist at that store.')
                        else:
                            price = float(input('Please enter the new price of the product: '))
                            self.sql.execute('''update carries
                                                set uprice = :price
                                                where :sid = sid and :pid = pid''',
                                             {'sid': sid, 'pid': pid, 'price':price})
                            self.conn.commit()
            print('\n')

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
        self.basket = []
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
            print('-- Logged in as ' + response[0][0] + ' --')
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