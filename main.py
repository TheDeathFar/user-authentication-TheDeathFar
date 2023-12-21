from src.biometric_system import BiometricSystem
from src.utils.key_listener import collect_data_for_input
from config import DB_HOST, DB_NAME, DB_PASS, DB_USER, DB_PORT

biometric_system = BiometricSystem(db_user=DB_USER,
                                   db_pass=DB_PASS,
                                   db_host=DB_HOST,
                                   db_port=DB_PORT,
                                   db_name=DB_NAME)


def identify_user():
    email = input('Enter your email: ')
    print('Enter your password: ')
    password, intervals, holdings_time = collect_data_for_input()

    user = {'email': email,
            'password': password,
            'intervals': intervals,
            'holdings_time': holdings_time}
    response = biometric_system.identify_user(data=user)
    print(response)


def register_user():
    email = input('Enter your email: ')
    print('Enter your password: ')
    password, intervals_i, holdings_time_i = collect_data_for_input()

    intervals = [intervals_i]
    holdings_time = [holdings_time_i]

    attempts = 3
    for i in range(attempts):
        print(f'Repeat your password ({attempts - i} times left): ')
        try:
            password_i, intervals_i, holdings_time_i = collect_data_for_input()
            if password == password_i:
                intervals.append(intervals_i)
                holdings_time.append(holdings_time_i)
            else:
                raise ValueError('Invalid password! Try one more time!')
        except ValueError as e:
            print(e)
            continue

    user = {'email': email,
            'password': password,
            'intervals': intervals,
            'holdings_time': holdings_time}
    response = biometric_system.register_user(data=user)
    print(response)


def main():
    while True:
        registered = input('Are you registered? (y/n/q): ')
        if registered.lower() == 'y':
            identify_user()
            break

        elif registered.lower() == 'n':
            register_user()
            break

        elif registered.lower() == 'q':
            break

        else:
            print('Invalid input. Please enter y, n, or q.')


if __name__ == '__main__':
    main()