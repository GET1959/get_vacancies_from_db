import psycopg2
from psycopg2 import Error
from config import config


PARAMS = config()


class DBManager:
    def __init__(self, db_name):
        PARAMS.update({"dbname": db_name})

    @staticmethod
    def get_companies_and_vacancies_count() -> list[tuple]:
        """
        Функция подсчитывает количество вакансий у каждой компании,
        возвращает список пар: (компания, количество вакансий)
        :return company list with vacancies amount:
        """
        try:
            with psycopg2.connect(**PARAMS) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """SELECT employers.company_name, COUNT(vacancies.vacancy_id)
                    FROM employers LEFT JOIN vacancies USING(employer_id) GROUP BY employers.company_name"""
                    )
                    return cursor.fetchall()
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if conn is not None:
                conn.close()

    @staticmethod
    def get_all_vacancies() -> list[tuple]:
        """
        Функция извлекает из базы данных информацию по каждой вакансии
        :return vacancy info:
        """
        try:
            with psycopg2.connect(**PARAMS) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """SELECT title, salary_from, salary_to, salary_norm, vacancies.url, employers.company_name
                        FROM vacancies LEFT JOIN employers USING(employer_id)"""
                    )
                    return cursor.fetchall()
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if conn is not None:
                conn.close()

    @staticmethod
    def get_avg_salary() -> int:
        """
        Функция рассчитывает среднюю зарплату по всем вакансиям базы, для расчета средней берется salary_norm.
        :return mean salary:
        """
        try:
            with psycopg2.connect(**PARAMS) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT SUM(salary_norm) / COUNT(salary_norm) FROM vacancies")
                    return int(cursor.fetchall()[0][0])
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if conn is not None:
                conn.close()

    @staticmethod
    def get_vacancies_with_higher_salary() -> list[tuple]:
        """
        Функция возвращает информацию о вакансиях с зарплатой выше средней.
        :return vacancy info:
        """
        try:
            with psycopg2.connect(**PARAMS) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """SELECT title, salary_from, salary_to, salary_norm, vacancies.url, employers.company_name
                            FROM vacancies LEFT JOIN employers USING(employer_id)
                            WHERE salary_norm > (SELECT SUM(salary_norm) / COUNT(salary_norm) FROM vacancies)"""
                    )
                    return cursor.fetchall()
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if conn is not None:
                conn.close()

    @staticmethod
    def get_vacancies_with_keyword(keyword: str) -> list[tuple]:
        """
        Функция принимает на вход ключевое слово и возвращает список вакансий, содержащих переданное слово
        :param keyword:
        :return vacancy info:
        """
        try:
            with psycopg2.connect(**PARAMS) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"""SELECT title, salary_from, salary_to, salary_norm, vacancies.url, employers.company_name
                        FROM vacancies LEFT JOIN employers USING(employer_id)WHERE title LIKE '%{keyword}%'"""
                    )
                    return cursor.fetchall()
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if conn is not None:
                conn.close()
