import os
import time


class Interface:
    """
    Controller class to manage user input
    """
    userID = -1;
    is_agent = 0;

    def __init__(self, conn, sql):
        self.conn = conn
        self.sql = sql

    def login_screen(self):
        os.system('clear')
        print('Login Menu')
        print('Customer Login: c')
        print('Agent Login: a')
        print('Logout: l')
        print('Register: r')
        print('Exit Program: e')
        response = input('Please select an action: ')
        options = {'c': self.customer_login,
                   'a': self.agent_login,
                   'l': self.logout,
                   'r': self.register,
                   'e': self.exit,
                   }
        try:
            options[response]()
        except KeyError:
            print('Invalid Input, please try again')
            time.sleep(1.5)
            self.login_screen()

    def customer_login(self):
        print('Customer Login')
        cid = input('ID: ')
        password = input('Password: ')
        self.sql.execute('''select c.cid
                        from customers c
                        where c.cid=:cid
                        and c.pwd=:pwd''',
                        {'cid':cid, 'pwd':password})
        response = self.sql.fetchall()
        print(response)

    def agent_login(self):
        print('Agent Login')
        aid = input('ID: ')
        password = input('Password: ')
        self.sql.execute('''select a.aid
                                from agents a
                                where a.aid=:aid
                                and a.pwd=:pwd''',
                         {'aid': aid, 'pwd': password})
        response = self.sql.fetchall()
        print(response)

    def logout(self):
        print('logout')

    def register(self):
        print('register')

    def exit(self):
        print('Exited Program')