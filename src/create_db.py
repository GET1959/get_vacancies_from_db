from typing import Any
import requests
import json
import time
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from config import config


with open("companies.json", "r", encoding="utf-8") as file:
    EMPLOYER_ID_LIST = list(json.load(file).values())
URL = "https://api.hh.ru/vacancies?"
HEADERS = {"HH-User-Agent": "get_vacancies_to_db (topchiev@mail.ru)"}
print(EMPLOYER_ID_LIST)


def get_currency_rate(currency: str) -> float:
    """
    Функция принимает наименование валюты для получения курса по API и возвращает ее курс к рублю.
    :param currency:
    :return currency_rate:
    """
    url_cur = "https://www.cbr-xml-daily.ru/daily_json.js"
    response = requests.get(url_cur)
    if response.status_code == 200:
        data = response.json()
        return data["Valute"][currency.upper()]["Value"] / data["Valute"][currency.upper()]["Nominal"]
    if currency.upper() == "USD":
        return 90
    elif currency.upper() == "EUR":
        return 100
    else:
        return 1


def normalize_salary(salary_from: Any, salary_to: Any, currency: float) -> int:
    """
    Функция принимает на вход данные по зарплате, полученные с сайта и возвращает значение зарплаты, в общем формате,
    приемлемом для сравнения.
    :param salary_from:
    :param salary_to:
    :param currency:
    :return salary_norm:
    """

    if not salary_from:
        salary_from = 0
    if not salary_to:
        salary_to = salary_from
    if currency == "RUR":
        salary_norm = max(salary_from, salary_to)
    else:
        salary_norm = int(max(salary_from, salary_to) * get_currency_rate(currency))

    return salary_norm


def create_db(db_name):
    """
    Функция создает базу данных компаний-работодателей с актуальными вакансиями.
    :return None:
    """
    params = config()
    print(params)
    conn = None
    try:
        conn = psycopg2.connect(**params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE {db_name}")
        print(f'Database {db_name} successfully created')
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if conn is not None:
            conn.close()

    params.update({"dbname": db_name})

    try:
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "CREATE TABLE employers(employer_id int PRIMARY KEY NOT NULL, company_name varchar, url varchar);"
                )
                cursor.execute(
                    """CREATE TABLE vacancies(vacancy_id int PRIMARY KEY NOT NULL, title varchar,
                    salary_from int, salary_to int, currency varchar, salary_norm int, url varchar,
                    employer_id int REFERENCES employers(employer_id));"""
                )
                for emp_id in EMPLOYER_ID_LIST:
                    response = requests.get(URL, headers=HEADERS, params={"employer_id": emp_id, "per_page": 100})
                    for item in response.json()["items"]:
                        if not item["salary"]:
                            continue
                        else:
                            salary_from = item["salary"]["from"]
                            salary_to = item["salary"]["to"]
                        if not salary_to:
                            salary_to = salary_from
                        if not salary_from:
                            salary_from = 0
                        currency = item["salary"]["currency"]
                        salary_norm = normalize_salary(salary_from, salary_to, currency)

                        cursor.execute(
                            """INSERT INTO employers (employer_id, company_name, url)
                            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING""",
                            (item["employer"]["id"], item["employer"]["name"], item["employer"]["alternate_url"]),
                        )

                        cursor.execute(
                            """INSERT INTO vacancies (vacancy_id, title, salary_from, salary_to, currency,
                            salary_norm, url, employer_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                            (
                                item["id"],
                                item["name"],
                                salary_from,
                                salary_to,
                                currency,
                                salary_norm,
                                item["alternate_url"],
                                item["employer"]["id"],
                            ),
                        )
                    time.sleep(0.2)
        print(f'Database {db_name} successfully filled')
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if conn:
            conn.close()
