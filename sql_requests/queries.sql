--1) Создание таблицы all_employers_id, в которой хранятся все найденные id компаний
CREATE TABLE all_employers_id
    (
    employer_id varchar(20) PRIMARY KEY,
    employer_name varchar(120) NOT NULL
    )

--2) Создание таблицы all_vacancies, в которой хранятся все найденные вакансии
CREATE TABLE all_vacancies
    (
    vacancie_id varchar(20) PRIMARY KEY,
    name varchar(200) NOT NULL,
    employer_id varchar(20) NOT NULL,
    employer_name varchar(200) NOT NULL,
    salary_from real,
    salary_to real,
    currency varchar(6),
    city varchar(300),
    description varchar,
    url varchar(2500)
    )

--3) Выборка с числом вакансий по каждой компании
SELECT employer_name, COUNT(*) FROM all_vacancies GROUP BY employer_name

--4) Выборка всех вакансий по указанным полям: employer_name, name, salary_from, salary_to, url
SELECT employer_name, name, salary_from, salary_to, url FROM all_vacancies

--5) Выборка всех зарплат, дляподсчета средней
SELECT salary_from, salary_to FROM all_vacancies

--6) Подсчет всех вакансий в таблице
SELECT COUNT(*) FROM all_vacancies