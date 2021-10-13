from typing import List

Employee = List[str]
Employees = List[Employee]


def works_on_position(employee: Employee, position: str) -> bool:
    if employee[7] == position:
        return True
    return False


def increase_payment_for_employees_on_position(
         employees: Employees,
         position: str,
         rate: float):
    filtered = [emp for emp in employees if works_on_position(emp, position)]
    for each in filtered:
        increase_payment_for_employee(each, rate)


def increase_payment_for_employee(employee: Employee, rate: float):
    payment = employee[5]
    payment = round(float(payment) * rate)
    employee[5] = str(payment)


def parse_file(file_name: str) -> Employees:
    with open(file_name, "r") as file:
        return [[value for value in employee.split(";")]
                for employee in file.readlines()]


def save_to_file(file_name: str, data: Employees):
    with open(file_name, "w") as file:
        file.writelines([";".join(employee) for employee in data])


DB_FILE = "employees.csv"
POSITION = "Web developer junior"
RATE = 1.15

emps = parse_file(DB_FILE)
increase_payment_for_employees_on_position(emps, POSITION, RATE)
save_to_file(DB_FILE, emps)
