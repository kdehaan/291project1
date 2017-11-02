
class Interface:
    """
    Controller class to manage user input
    """
    screen = 'Login'

    def __init__(self):
        print(self.screen)

    def login_screen(self):

        print('Customer Login: c')
        print('Agent Login: a')
        print('Logout: l')
        print('Register: r')
        print('Exit Program: e')
        response = input('Please select an action: ')
        options = {'c': self.customer_login(),
                   'a': self.agent_login(),
                   'l': self.logout(),
                   'r': self.register(),
                   'e': self.exit(),
                   }
        try:
            options[response]()
        except KeyError:
            print('invalid input')
            self.login_screen()

    def customer_login(self):
        print('customer_login')

    def agent_login(self):
        print('agent_login')

    def logout(self):
        print('logout')

    def register(self):
        print('register')

    def exit(self):
        print('exit')