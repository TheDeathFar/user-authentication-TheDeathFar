from __future__ import annotations

import scipy
from scipy import stats as st
import numpy as np


def hamming_mera(current_data: list[float], min_data: list[float], max_data: list[float]):
    """
    Метод для вычисления расстояния Хэмминга между текущими данными и эталонными данными.
    :param current_data: текущие данные.
    :param min_data: минимальные эталонные данные.
    :param max_data: максимальные эталонные данные.
    :return: расстояние Хэмминга.
    """
    current_data = np.array(current_data)
    min_data = np.array(min_data)
    max_data = np.array(max_data)
    distance = sum(1 for i in range(len(current_data)) if not (min_data[i] <= current_data[i] <= max_data[i]))
    return distance


def min_max_columns(X: list[list[float]]):
    """
    Функция ищет минимальные и максимальные значения по столбцам матрицы.
    :param X: матрица значений.
    :return: кортеж из минимальных и максимальных значений по столбцам.
    """
    matrix = np.array(X)
    if len(matrix) == 0:
        return None, None

    min_values = np.min(matrix, axis=0)
    max_values = np.max(matrix, axis=0)

    return min_values, max_values