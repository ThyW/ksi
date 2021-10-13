from typing import List


class Person():
    def __init__(self,
                 person_id: int,
                 name: str,
                 age: int,
                 accounts: List['Account']):  # '' protože typ bude definován
        self.person_id: int = person_id
        self.name: str = name
        self.age: int = age
        self.accounts: List['Account'] = accounts

    def check_integrity(self) -> bool:
        test = []
        for each in self.accounts:
            if each.owner == self:
                test.append(True)
            else:
                test.append(False)
        if self.age >= 18 and self.name and all(test):
            return True
        return False


class Account():
    def __init__(self, account_id: int,
                 password: str,
                 balance: int,
                 limit: int,
                 owner: Person):
        self.account_id: int = account_id
        self.password: str = password
        self.balance: int = balance
        self.limit: int = limit
        self.owner: Person = owner

    def add_balance(self, password: str, amount: int) -> bool:
        if password == self.password and\
                self.balance + amount <= self.limit and amount > 0:
            self.balance += amount
            return True
        return False

    def withdraw_balance(self, password: str, amount: int) -> bool:
        if password != self.password or amount > 100000 or\
                self.balance - amount < 0:
            return False
        self.balance -= amount
        return True

    def set_limit(self, password: str, new_limit: int) -> bool:
        if self.password != password:
            return False
        self.limit = new_limit
        return True

    def total_remaining(self) -> int:
        return self.balance
