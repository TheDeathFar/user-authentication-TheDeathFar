import random
from string import ascii_lowercase, ascii_uppercase, punctuation, digits
import unittest
import json
from sqlalchemy import delete
from src.biometric_system import BiometricSystem
from config import DB_HOST, DB_NAME, DB_PASS, DB_USER, DB_PORT


# функция для генерации пароля заданной длины
def generate_password(length: int):
    alphabets = list(f'{ascii_lowercase}{ascii_uppercase}{digits}')
    return ''.join([random.choice(alphabets) for _ in range(length)])


# функция для генерации данных пользователей в формате JSON
def generate_users_to_json():
    users_data = []
    num_of_users = 5
    for i in range(num_of_users):
        password = generate_password(7)
        user_data = {}
        user_data.update({'email': f'test_{i}@email.com'})
        user_data.update({'password': password})
        attempts = 4
        # генерируем случайные интервалы между нажатиями клавиш и времена удерживания клавиш для каждой попытки
        user_data.update({'intervals':
                              [[random.normalvariate(0.5, 0.16) for _ in range(len(password) - 1)]
                               for _ in range(attempts)]})
        user_data.update({'holdings_time':
                              [[random.normalvariate(0.3, 0.05) for _ in range(len(password))]
                               for _ in range(attempts)]})
        users_data.append(user_data)
    # записываем данные пользователей в файл в формате JSON
    with open('test_users.json', 'w') as file:
        file.write(json.dumps(users_data, indent=4))


# класс для тестирования функционала биометрической системы
class TestTask(unittest.TestCase):
    def setUp(self):
        # создаем экземпляр биометрической системы для тестирования
        self.biometric_system = BiometricSystem(db_user=DB_USER,
                                                db_pass=DB_PASS,
                                                db_host=DB_HOST,
                                                db_port=DB_PORT,
                                                db_name=DB_NAME)
        # генерируем данные пользователей и записываем их в файл
        generate_users_to_json()
        with open('test_users.json', 'rb') as f:
            self.users_data = json.load(f)

    # тест на регистрацию пользователей и их идентификацию
    def test_registration_and_identification(self):
        # регистрируем каждого пользователя и проверяем успешность операции
        for user_data in self.users_data:
            result = self.biometric_system.register_user(data=user_data)
            print(f"Registration for {user_data.get('email')}: {result}")
            self.assertEqual('success', result['status'])

        # для каждого пользователя проверяем, что его клавиатурный почерк определяется системой корректно
        for user_data in self.users_data:
            # имитируем почерк, передавая первые значения биометрических данных
            intervals = user_data['intervals'][0]
            holdings_time = user_data['holdings_time'][0]

            user = {'email': user_data['email'],
                    'password': user_data['password'],
                    'intervals': intervals,
                    'holdings_time': holdings_time}
            result = self.biometric_system.identify_user(data=user)
            print(f"Identification for {user_data.get('email')}: {result}")
            self.assertEqual('permit', result['status'])

    def tearDown(self):
        session = self.biometric_system.db.get_session()
        try:
            for user_data in self.users_data:
                stmt = delete(self.biometric_system.db.user_table).\
                    where(self.biometric_system.db.user_table.c.email == str(user_data['email']).strip())
                session.execute(stmt)
                session.commit()
        except Exception as e:
            print(e)
            session.rollback()
        finally:
            session.close()


if __name__ == '__main__':
    unittest.main()
