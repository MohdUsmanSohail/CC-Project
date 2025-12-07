load employees from "employees.csv"

filter high_salary {
    salary > 50000
}

map on high_salary {
    bonus = salary * 50000
}