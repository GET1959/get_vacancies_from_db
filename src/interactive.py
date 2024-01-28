from datetime import datetime
from typing import Any
from src.db_manager import DBmanager


GREETING = (
    "Доброе утро!" * (4 <= datetime.now().hour < 11)
    + "Добрый день!" * (11 <= datetime.now().hour < 16)
    + "Добрый вечер!" * (16 <= datetime.now().hour < 23)
    + "Доброй ночи!" * (datetime.now().hour == 23)
    + "Доброй ночи!" * (0 <= datetime.now().hour < 4)
)


def declension(number: int, word: str, word_1: str, word_2: str) -> str:
    """
    Функция принимает на вход число и три варианта склонения слова и возвращает корректный вариант
    для введенного числа.
    :param number:
    :param word:
    :param word_1:
    :param word_2:
    :return word in right declension:
    """
    return (
        word * (str(number)[-1] == "1" and number % 100 != 11)
        + word_1 * (str(number)[-1] in ["2", "3", "4"] and number % 100 not in [12, 13, 14])
        + word_2 * (str(number)[-1] in ["0", "5", "6", "7", "8", "9"] or number % 100 in [11, 12, 13, 14])
    )


def user_func(database: Any) -> None:
    """
    Функция выводит вакансии на основании пользовательского ввода.
    :return None:
    """
    print(GREETING)
    print(
        """В этом приложении вы можете получить список актуальных вакансий
    с сайта hh.ru от наиболее востребованных работодателей."""
    )
    print()
    print("Чтобы получить список работодателей и количество их актуальных вакансий, введите 1")
    print("Чтобы получить информацию обо всех актуальных вакансиях, введите 2")
    print("Чтобы получить среднюю зарплату по найденным вакансиям, введте 3")
    print("Чтобы получить информацию о вакансиях с зарплатой выше средней, введите 4")
    print("Чтобы получить список вакансий по ключевому слову, введите ключевое слово")

    dbm = DBmanager(database)

    user_input = input()
    if user_input == "1":
        for company in dbm.get_companies_and_vacancies_count():
            print(f"{company[0]} - {company[1]} {declension(company[1], 'вакансия', 'вакансии', 'вакансий')}")

    elif user_input == "2":
        for vac in dbm.get_all_vacancies():
            print(f"{vac[0]}, зарплата от {vac[1]} до {vac[2]}, url: {vac[4]}, {vac[5]}.")
        a = len(dbm.get_all_vacancies())
        print(f"Всего {a} {declension(a, 'вакансия', 'вакансии', 'вакансий')}")

    elif user_input == "3":
        a = dbm.get_avg_salary()
        print(f"Средняя зарплата по найденным вакансиям составляет {a} {declension(a, 'рубль', 'рубля', 'рублей')}")

    elif user_input == "4":
        for vac in dbm.get_vacancies_with_higher_salary():
            print(f"{vac[0]}, зарплата от {vac[1]} до {vac[2]}, url: {vac[4]}, {vac[5]}.")
        a = len(dbm.get_vacancies_with_higher_salary())
        print(f"Всего {a} {declension(a, 'вакансия', 'вакансии', 'вакансий')}")

    else:
        for vac in dbm.get_vacancies_with_keyword(keyword=user_input):
            print(f"{vac[0]}, зарплата от {vac[1]} до {vac[2]}, url: {vac[4]}, {vac[5]}.")
        a = len(dbm.get_vacancies_with_keyword(user_input))
        print(f"Всего {a} {declension(a, 'вакансия', 'вакансии', 'вакансий')}")
