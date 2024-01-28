from src.create_db import create_db
from src.interactive import user_func


database = "vacancy_db"


def main():
    create_db(database)
    user_func(database)


if __name__ == "__main__":
    main()
