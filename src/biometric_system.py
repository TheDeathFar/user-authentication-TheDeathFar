from datetime import datetime, timedelta
from sqlalchemy import select
from pydantic import ValidationError
from src.db.my_db import PostgresDB
import numpy as np
from src.utils.hash_code import HashCode
from src.db.validation import UserValidator
from src.utils.my_math import hamming_mera, min_max_columns


class BiometricSystem:
    def __init__(self, *,
                 db_user: str,
                 db_pass: str,
                 db_host: str,
                 db_port: int,
                 db_name: str):

        # Создать экземпляр класса PostgresDB
        self._db = PostgresDB(db_user=db_user,
                              db_pass=db_pass,
                              db_host=db_host,
                              db_port=db_port,
                              db_name=db_name)

    def register_user(self, *, data: dict):

        try:
            # Валдиация введённых данных пользователя
            UserValidator(**data)

            # Получение текущую дату и время
            registered_at = datetime.now()

            # Хэширование пароля с помощью класса HashCode
            password = data['password']
            password = HashCode(password=password, salt=registered_at.strftime('%Y-%m-%d'))
            registered_at = registered_at

            # Минимальные и максимальные интервалы
            min_intervals, max_intervals = min_max_columns(data['intervals'])

            # Минимальное и максимальное время удержания
            min_holdings_time, max_holdings_time = min_max_columns(data['holdings_time'])

            # Добавляем пользователя в базу данных
            session = self.db.get_session()
            new_user = {'email': data['email'],
                        'registered_at': registered_at.isoformat(),
                        'password': password,
                        'min_intervals': min_intervals,
                        'max_intervals': max_intervals,
                        'min_holdings_time': min_holdings_time,
                        'max_holdings_time': max_holdings_time}

            with self.db.engine.connect() as conn:
                query = select(self.db.user_table).where(self.db.user_table.c.email == str(data['email'].strip()))
                user_obj = conn.execute(query).fetchone()
            try:
                if user_obj is None:
                    insert_stmnt = self.db.user_table.insert().values(**new_user)
                    session.execute(insert_stmnt)
                    session.commit()
                    return {'status': 'success'}
                else:
                    print('User already exists!')
                    return {'status': 'fail'}
            except Exception as e:
                print(e)
                session.rollback()
                return {'status': 'fail'}
            finally:
                session.close()
        except ValidationError as e:
            print(e)
            return {'status': 'fail'}

    def identify_user(self, *, data: dict):
        with self.db.engine.connect() as conn:
            query = select(self.db.user_table).where(self.db.user_table.c.email == str(data['email'].strip()))
            user_obj = conn.execute(query).fetchone()

            if user_obj is None:
                raise ValueError('User does not exist!')

            user_data = {'email': str(user_obj[0]),
                         'registered_at': str(user_obj[1]),
                         'password': str(user_obj[2]),
                         'min_intervals': list(user_obj[3]),
                         'max_intervals': list(user_obj[4]),
                         'min_holdings_time': list(user_obj[5]),
                         'max_holdings_time': list(user_obj[6])}
            try:
                # Генерируется хэш для введённого пароля и сравнивается с сохраненным
                password = HashCode(password=data['password'], salt=user_data['registered_at'])
                if password != user_data['password']:
                    print()
                    raise ValueError('Неверный пароль!')

                # Рассчитать меру Хэмминга для интервалов
                current_intervals = data['intervals']
                min_intervals = user_data['min_intervals']
                max_intervals = user_data['max_intervals']
                distance_intervals = hamming_mera(current_intervals, min_intervals, max_intervals)

                # Рассчитать меру Хэмминга для времени удержания
                current_holdings_time = data['holdings_time']
                min_holdings_time = user_data['min_holdings_time']
                max_holdings_time = user_data['max_holdings_time']
                distance_holdings_time = hamming_mera(current_holdings_time, min_holdings_time, max_holdings_time)

                if distance_intervals >= 0.7 * len(current_intervals) or distance_holdings_time >= 0.7 * len(current_holdings_time):
                    raise ValueError('Нетипичное время удержания клавиш или интервалы между нажатиями!')
                else:
                    return {'status': 'permit'}

            except ValueError as e:
                print(e)
                return {'status': 'refuse'}
            except Exception as e:
                print(e)
                return {'status': 'refuse'}

    @property
    def db(self):
        return self._db

    @property
    def expiring(self):
        return self._expiring

    @expiring.setter
    def expiring(self, value: int):
        assert type(value) is int and value > 0
        self._expiring = value
