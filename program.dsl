load employees from "employees.csv"

filter high_salary {
    where salary > 50000
}

map bonus_calc on high_salary {
    bonus = salary * 0.10
}

aggregate stats on bonus_calc {
    avg_salary = avg(salary)
    avg_bonus = avg(bonus)
}

print stats

for row in bonus_calc {
    print row.name, row.salary, row.bonus
}