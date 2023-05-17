import psycopg2
import requests


import utils as ut


class GetReguestError(Exception):
    """Класс-исключение для обработки ошибок при запросе к сайту"""

    def __init__(self, status_code, platform):
        self.status_code = status_code
        self.platform = platform

    def __str__(self):
        return f'Ошибка запроса к площадке {self.platform}. Код ошибки: {self.status_code}'


class HH:
    """Класс для парсинга платформы HeadHunter"""

    def get_request(self, keyword: str | None, employer_id: str | list, page: int):
        """
        метод отправки запроса и получения информации с сайта https://api.hh.ru/vacancies
        :param employer_id: список id компаний-работадателей, по которым будет производиться поиск
        :param keyword: слово/слова, которые необходимо найти в тексте вакансии
        :param page: текущая страница с результатами
        :return: список с данными вакансий с текущей страницы или исключение GetReguestError
        """
        url = "https://api.hh.ru/vacancies"
        params = {
            "text": keyword,
            "page": page,
            "per_page": 100,
            "employer_id": employer_id
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()['items']
        else:
            raise GetReguestError(response.status_code, 'HeadHunter')

    def get_vacancies(self, keyword: str | None, employer_id: str | list, count: int = 1000):
        """
        метод для добавления всех найденных вакансий в общий список
        :param employer_id: список id компаний-работадателей, по которым будет производиться поиск
        :param keyword: слово/слова, которые необходимо найти в тексте вакансии
        :param count: общее количество вакансий (округляется кратно 100 в большую сторону), не более 1000
        :return: список с данными вакансий со всех страниц или исключение GetReguestError
        """
        pages = count // 100 if count % 100 == 0 else count // 100 + 1
        all_vacancies = []
        for page in range(pages):
            print('Парсинг страницы', page + 1)
            vacancies_per_page = self.get_request(keyword, employer_id, page)
            if type(vacancies_per_page) is str:
                return vacancies_per_page
            all_vacancies.extend(vacancies_per_page)
        return all_vacancies

    def get_request_employers_id(self, keyword, page):
        """
        метод отправки запроса и получения информации с сайта https://api.hh.ru/employers
        :param keyword: слово/слова, которые необходимо найти в названии компании
        :param page: текущая страница с результатами
        :return: список словарей, где ключ - id, значение - название компании
        """
        url = "https://api.hh.ru/employers"
        params = {
            "text": keyword,
            "page": page,
            "per_page": 100,
        }
        response = requests.get(url, params=params)
        id_from_page = []
        if response.status_code == 200:
            for employer in response.json()['items']:
                id_from_page.append({int(employer['id']): employer['name']})
        return id_from_page

    def select_employers_id(self, employers_list: list, pages=10):
        """
        метод для создания списка id компаний по выбранным ключевым словам
        :param employers_list: список названий компаний
        :param pages: текущая страница
        :return: список словарей, где ключ - id, значение - название компании
        """
        all_employers_id = []
        for employer in employers_list:
            for i in range(pages):
                if self.get_request_employers_id(keyword=employer, page=i):
                    for results in self.get_request_employers_id(keyword=employer, page=i):
                        all_employers_id.append(results)
        return all_employers_id


class DBManager:

    connect = psycopg2.connect(
        host="localhost",
        database="HH_vacancies",
        user="postgres",
        password="4444"
    )

    def create_table_all_employers_id(self, connect=connect):
        """метод создает таблицу all_employers_id со всеми компаниями, если таблица создана печатает сообщение"""
        try:
            with connect:
                with connect.cursor() as cur:
                    cur.execute(f"CREATE TABLE all_employers_id\n"
                                f"(employer_id varchar(20) PRIMARY KEY,"
                                f"employer_name varchar(120) NOT NULL)")

            #connect.close()
            print('Table "all_employers_id" was created')
        except:
            print('Table "all_employers_id" already existing')

    def insert_all_employers_id(self, employers_list: list, connect=connect):
        """
        метод вставляет данные о компаниях из списка в таблицу all_employers_id
        :param employers_list: список компаний
        :return: None
        """
        a = HH()
        selected_employers_id = a.select_employers_id(employers_list)
        with connect:
            with connect.cursor() as cur:
                for employer in selected_employers_id:
                    for employer_id, employer_name in employer.items():
                        try:
                            cur.execute(f"INSERT INTO all_employers_id VALUES "
                                        f"('{employer_id}', '{employer_name}');")
                        except:
                            continue
        #connect.close()
        print('Table "all_employers_id" was updated')

    def create_table_selected_employers_id(self, connect=connect):
        """метод создает таблицу 'selected_employers_id' из 'all_employers_id' по выбранным id"""
        selected_id = ut.get_selected_employers_id()
        str_selected_id = ut.get_str_from_list(selected_id)
        try:
            with connect:
                with connect.cursor() as cur:
                    cur.execute(f"CREATE TABLE selected_employers_id AS "
                                f"SELECT * FROM all_employers_id WHERE employer_id in {str_selected_id};")
            #connect.close()
            print('Table "selected_employers_id" was created')
        except:
            print('Table "selected_employers_id" already existing')

    def get_selected_employers_id(self, connect=connect):
        """возвращает список id из таблиы 'selected_employers_id'"""
        result = []
        with connect:
            with connect.cursor() as cur:
                cur.execute(f"SELECT employer_id FROM selected_employers_id;")
                for i in cur.fetchall():
                    for j in i:
                        result.append(j)
        #connect.close()
        return result

    def create_table_all_vacancies(self, connect=connect):
        """создает таблицу 'all_vacancies'"""
        with connect:
            with connect.cursor() as cur:
                try:
                    cur.execute(f"CREATE TABLE all_vacancies\n"
                                f"(vacancie_id varchar(20) PRIMARY KEY,"
                                f"name varchar(200) NOT NULL,"
                                f"employer_id varchar(20) NOT NULL,"
                                f"employer_name varchar(200) NOT NULL,"
                                f"salary_from real,"
                                f"salary_to real,"
                                f"currency varchar(6),"
                                f"city varchar(300),"
                                f"description varchar,"
                                f"url varchar(2500));")
                    print(f'Table "all_vacancies" was created')
                except:
                    print(f'Table "all_vacancies" already existing')
        #connect.close()

    def insert_data_to_all_vacancies(self, data: list, connect=connect):
        """создает таблицу 'all_vacancies'"""
        with connect:
            with connect.cursor() as cur:
                for i in data:
                    vacancie_id = i.get('id')
                    name = i.get('name')
                    employer_id = i.get('employer').get('id')
                    employer_name = i.get('employer').get('name')
                    if not i.get('salary'):
                        salary_to, salary_from, currency = 0, 0, None
                    else:
                        salary_from = i.get('salary').get('from') if i.get('salary').get('from') else 0
                        salary_to = i.get('salary').get('to') if i.get('salary').get('to') else 0
                        currency = i.get('salary').get('currency') if i.get('salary') else None
                    city = i.get('area').get('name')
                    description = ut.change_ap(i.get('snippet').get('responsibility')) if i.get('snippet').get('responsibility') else None
                    url = i.get('alternate_url')
                    try:
                        cur.execute(f"INSERT INTO all_vacancies VALUES "
                                    f"('{vacancie_id}', '{name}', '{employer_id}', '{employer_name}', '{salary_from}', "
                                    f"'{salary_to}', '{currency}', '{city}', '{description}', '{url}');")
                    except:
                        continue
                print(f'Table "all_vacancies" was updated')
        #connect.close()

    def get_companies_and_vacancies_count(self, connect=connect):
        """получает список всех компаний и количество вакансий у каждой компании"""
        with connect:
            with connect.cursor() as cur:
                cur.execute("SELECT employer_name, COUNT(*) FROM all_vacancies GROUP BY employer_name")
                result = cur.fetchall()
        #connect.close()
        return result

    def get_all_vacancies(self, connect=connect):
        """получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию."""
        with connect:
            with connect.cursor() as cur:
                cur.execute("SELECT employer_name, name, salary_from, salary_to, url FROM all_vacancies")
                result = cur.fetchall()
        #connect.close()
        return result

    def get_avg_salary(self, connect=connect):
        """получает среднюю зарплату по вакансиям."""
        with connect:
            with connect.cursor() as cur:
                cur.execute("SELECT salary_from, salary_to FROM all_vacancies")
                result = cur.fetchall()
        #connect.close()
        salary_list = []
        for pair in result:
            a, b = pair
            if a == 0 and b == 0:
                continue
            elif a != 0 and b != 0:
                salary_list.append((a + b)/2)
            else:
                salary_list.append(abs(a - b))
        return sum(salary_list) / len(salary_list)

    def get_vacancies_with_higher_salary(self, connect=connect):
        """получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""
        avg_salary = self.get_avg_salary()
        with connect:
            with connect.cursor() as cur:
                cur.execute(f"SELECT * FROM all_vacancies WHERE salary_from > {avg_salary} OR salary_to > {avg_salary}")
                result = cur.fetchall()
        #connect.close()
        return result

    def get_vacancies_with_keyword(self, keyword: str, connect=connect):
        """получает список всех вакансий, в названии которых содержатся переданные в метод слова, например 'python'."""
        with connect:
            with connect.cursor() as cur:
                cur.execute(f"SELECT * FROM all_vacancies "
                            f"WHERE name LIKE ('%{keyword.lower()}%') OR name LIKE ('%{keyword.capitalize()}%')")
                result = cur.fetchall()
        #connect.close()
        return result

    def get_count_of_all(self, connect=connect):
        """получает число всех вакансий в базе"""
        with connect:
            with connect.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM all_vacancies")
                result = cur.fetchall()
        #connect.close()
        return result[0][0]
