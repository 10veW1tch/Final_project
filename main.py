import uuid
from datetime import datetime, timezone
from typing import Optional, List


class Transaction:
    
    def __init__(
        self,
        id: uuid.UUID,
        type: str,
        sender_name: Optional[str],
        receiver_name: Optional[str],
        amount: int,
        status: str,
        timestamp: datetime,
    ) -> None:
        self.id = id
        self.type = type
        self.sender_name = sender_name
        self.receiver_name = receiver_name
        self.amount = amount
        self.status = status
        self.timestamp = timestamp

    def __str__(self) -> str:
        return f"{self.timestamp.isoformat()} | {self.type.upper()} | {self.amount} | {self.status} | from: {self.sender_name or '-'} to: {self.receiver_name or '-'} | id: {self.id}"


class BankAccount:
    def __init__(
        self,
        id: uuid.UUID,
        name: str,
        account_number: str,
        balance: int,
        created_at: datetime,
    ) -> None:
        self.id = id
        self.name = name
        self.account_number = account_number
        self.balance = balance
        self.created_at = created_at
        self.transactions: List[Transaction] = []
        self.is_closed = False

    def __str__(self) -> str:
        status = "CLOSED" if self.is_closed else "ACTIVE"
        return f"Account({self.name}, No.{self.account_number}, balance={self.balance}, status={status})"

    def record_transaction(
        self,
        t_type: str,
        sender_name: Optional[str],
        receiver_name: Optional[str],
        amount: int,
        status: str,
    ) -> Transaction:
        t = Transaction(
            id=uuid.uuid4(),
            type=t_type,
            sender_name=sender_name,
            receiver_name=receiver_name,
            amount=amount,
            status=status,
            timestamp=datetime.now(timezone.utc),
        )
        self.transactions.append(t)
        return t

    def deposit(self, amount: int) -> None:
        if self.is_closed:
            print("This account is closed. Operation not allowed.")
            return
        if amount <= 0:
            print("Amount must be positive.")
            self.record_transaction("deposit", None, self.name, amount, "failed")
            return
        self.balance += amount
        self.record_transaction("deposit", None, self.name, amount, "completed")
        print(f"Deposited {amount}. New balance: {self.balance}")

    def withdraw(self, amount: int) -> None:
        if self.is_closed:
            print("This account is closed. Operation not allowed.")
            return
        if amount <= 0:
            print("Amount must be positive.")
            self.record_transaction("withdraw", self.name, None, amount, "failed")
            return
        if amount > self.balance:
            print("Insufficient funds.")
            self.record_transaction("withdraw", self.name, None, amount, "failed")
            return
        self.balance -= amount
        self.record_transaction("withdraw", self.name, None, amount, "completed")
        print(f"Withdrawn {amount}. New balance: {self.balance}")

    def show_transactions(self) -> None:
        print(f"=== Transactions for {self.name} ({self.account_number}) ===")
        if not self.transactions:
            print("No transactions.")
        else:
            for t in self.transactions:
                print(str(t))
        print("===============================")

    def close_account(self) -> None:
        if self.is_closed:
            print("Account is already closed.")
            return
        self.record_transaction("close", self.name, None, self.balance, "completed")
        self.balance = 0
        self.is_closed = True
        self.name = f"{self.name} (Closed)"
        print(f"Account {self.account_number} has been closed and balance reset to zero.")


def find_account_by_number(account_number: str, accounts: List[BankAccount]) -> Optional[BankAccount]:
    for acc in accounts:
        if acc.account_number == account_number:
            return acc
    return None


def list_accounts_brief(accounts: List[BankAccount]) -> None:
    if not accounts:
        print("No accounts yet.")
        return
    for i, acc in enumerate(accounts, start=1):
        status = "CLOSED" if acc.is_closed else "ACTIVE"
        print(f"{i}. {acc.name} | No. {acc.account_number} | Balance: {acc.balance} | {status}")


accounts: List[BankAccount] = []


def create_account() -> BankAccount:
    print("Create a new account.")
    name = input("Account holder name: ").strip()
    account_number = input("Account number (press Enter to auto-generate): ").strip()
    if not account_number:
        account_number = uuid.uuid4().hex[:10].upper()
        print(f"Generated account number: {account_number}")
    while True:
        try:
            balance = int(input("Initial balance: "))
            break
        except ValueError:
            print("Enter an integer.")
    acc = BankAccount(uuid.uuid4(), name, account_number, balance, datetime.now(timezone.utc))
    accounts.append(acc)
    if balance > 0:
        acc.record_transaction("deposit", None, acc.name, balance, "completed")
    print(f"Account {acc.account_number} created successfully.")
    return acc


def deactivate_account() -> None:
    list_accounts_brief(accounts)
    acc_num = input("Enter account number to deactivate: ").strip()
    acc = find_account_by_number(acc_num, accounts)
    if not acc:
        print("Account not found.")
        return
    confirm = input(f"Are you sure you want to close {acc.name}? (yes/no): ").lower()
    if confirm == "yes":
        acc.close_account()
    else:
        print("Operation cancelled.")


menu_text = """=== Bank System Menu ===
1. Create New Account
2. View All Accounts
3. Search Account
4. Deposit
5. Withdraw
6. View Transactions
7. Close Account
8. Exit
========================"""


def main_menu() -> None:
    while True:
        print("\n" + menu_text)
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            create_account()
        elif choice == "2":
            list_accounts_brief(accounts)
            input("Press Enter to return...")
        elif choice == "3":
            term = input("Enter name or account number: ").strip().lower()
            found = [a for a in accounts if term in a.name.lower() or term in a.account_number.lower()]
            if not found:
                print("No results.")
            else:
                for acc in found:
                    print(acc)
            input("Press Enter to return...")
        elif choice == "4":
            list_accounts_brief(accounts)
            num = input("Enter account number: ").strip()
            acc = find_account_by_number(num, accounts)
            if acc:
                amt = int(input("Deposit amount: "))
                acc.deposit(amt)
            else:
                print("Account not found.")
        elif choice == "5":
            list_accounts_brief(accounts)
            num = input("Enter account number: ").strip()
            acc = find_account_by_number(num, accounts)
            if acc:
                amt = int(input("Withdraw amount: "))
                acc.withdraw(amt)
            else:
                print("Account not found.")
        elif choice == "6":
            list_accounts_brief(accounts)
            num = input("Enter account number: ").strip()
            acc = find_account_by_number(num, accounts)
            if acc:
                acc.show_transactions()
                input("Press Enter to return...")
            else:
                print("Account not found.")
        elif choice == "7":
            deactivate_account()
        elif choice == "8":
            print("Exiting system.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main_menu()

