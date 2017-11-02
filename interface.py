import time


class Interface:
    """
    Controller class to manage user input
    """
    userID = -1
    is_agent = 0
    states = {}  # contains the state machine
    state = 'l'

    def __init__(self, conn, sql):
        self.conn = conn
        self.sql = sql
        self.states = {'l': self.login_screen,
                       'c': self.customer_login,
                       'a': self.agent_login,
                       'o': self.logout,
                       'r': self.register,
                       'e': self.exit}
        self.run()

    def run(self):

        while True:
            selection = self.states[self.state]().lower()
            if selection in self.states:
                self.state = selection
            else:
                print("Invalid Selection")
                time.sleep(0.4)

    def login_screen(self):
        print('\n~~~~ Login Menu ~~~~')
        print('Customer Login: c')
        print('Agent Login: a')
        print('Logout: o')
        print('Register: r')
        print('Exit Program: e')
        selection = input('Please select an action: ')

        options = {'c': 'c',
                   'a': 'a',
                   'o': 'o',
                   'r': 'r',
                   'e': 'e'}
        try:
            return options[selection]
        except KeyError:
            return 'invalid'

    def customer_login(self):
        print('\n~~~~ Customer Login ~~~~~')
        cid = input('ID: ')
        password = input('Password: ')
        self.sql.execute('''select c.cid
                        from customers c
                        where c.cid=:cid
                        and c.pwd=:pwd''',
                        {'cid': cid, 'pwd': password})
        response = self.sql.fetchall()
        if not response:
            print("Invalid ID or Password")
            time.sleep(0.4)
            state = input("Try again? [y/n]")
            if state == 'n':
                return 'l'
            else:
                return 'c'
        else:
            print(response[0])
            return 'l'

    def agent_login(self):
        print('\n~~~~ Agent Login ~~~~')
        aid = input('ID: ')
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
            state = input("Try again? [y/n]")
            if state == 'n':
                return 'l'
            else:
                return 'a'
        else:
            print(response[0])
            return 'l'

    def logout(self):
        print('logout')

    def register(self):
        print('register')

    def exit(self):
        print('Exited Program')