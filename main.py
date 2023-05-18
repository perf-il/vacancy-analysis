from classes import DBManager, HH
import utils as ut


data = DBManager()
hh_agent = HH()
user_input = None

print(f'Перед вами программа для работы с базой данных PostgreSQL.\n'
      f'После подтверждения, будет созданна база данных вакансий компаний, id которых хранятся'
      f' в файле ./data/selected_employers_id.json\n')

input('Для продолжения нажмите Enter')

data.create_table_selected_employers_id()
data.insert_table_selected_employers_id()
data.create_table_all_vacancies()

for i in ut.get_selected_employers_id():
    print(f'\nПоиск вакансий компании: {hh_agent.get_name_employer_per_id(i)}')
    data_vac = hh_agent.get_vacancies(keyword=None, employer_id=i)
    data.insert_data_to_all_vacancies(data_vac)

print(f'База данных с  вакансиями успешно создана.\n'
      f'В настоящий момент в базе хранится таблица all_vacancies с {data.get_count_of_all()} вакансиями\n')

print('Вам доступны следующие функции для работы с базой:\n'
      '1. Получить список всех компаний с количеством вакансий\n'
      '2. Получить список всех вакансий с краткой информацией\n'
      '3. Получитт среднюю зарплату по всем вакансиям\n'
      '4. Получить список всех вакансий, у которых зарплата выше средней\n'
      '5. Поиск по ключевому слову\n'
      '6. Получить список выбранных компаний с их ID')

#  цикл для работы с запросами по базе
while user_input != '0':
    user_input = input('\nВведите число от 1 до 6 или 0 для выхода: ').strip().lower()
    if user_input == '1':
        print()
        print('Название - Вакансий')
        for name, count in data.get_companies_and_vacancies_count():
            print(f'{name} - {count}')
    elif user_input == '2':
        print()
        print('Компания - Название вакансии - Зарплата от - Зарплата до - Ссылка на вакансию')
        for company, name, salary_from, salary_to, url in data.get_all_vacancies():
            print(f'{company} - {name} - {salary_from} - {salary_to} - {url}')
    elif user_input == '3':
        print()
        print(f'Средня зарплата по всем вакансиям составляет {data.get_avg_salary()} рублей')
    elif user_input == '4':
        print()
        print('ID вакансии - Название вакансии - Компания - Зарплата от - Зарплата до - Валюта - Город - '
              'Описание вакансии - Ссылка на вакансию')
        for vac in data.get_vacancies_with_higher_salary():
            print(f'{vac[0]} - {vac[1]} - {vac[3]} - {vac[4]} - {vac[5]} - {vac[6]} - {vac[7]} - {vac[8]} - {vac[9]}')
        print(f'Всего найдено {len(data.get_vacancies_with_higher_salary())} вакансий')
    elif user_input == '5':
        print()
        keyword = input('Введите ключевое слово: ').strip().lower()
        for vac in data.get_vacancies_with_keyword(keyword):
            print(f'{vac[0]} - {vac[1]} - {vac[3]} - {vac[4]} - {vac[5]} - {vac[6]} - {vac[7]} - {vac[8]} - {vac[9]}')
        print(f'Всего найдено {len(data.get_vacancies_with_keyword(keyword))} вакансий')
    elif user_input == '6':
        print()
        print('ID компании - Название')
        i = 0
        for company_id, company_name in data.get_selected_employers():
            print(f'{i + 1} - {company_id} - {company_name}')
            i += 1
    else:
        if user_input != '0':
            print('Некорректный ввод\n')
