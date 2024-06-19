
'''OOP version
Use python OOP_app.py + "command" to run the program'''


# We need to create an account before creating the user



from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Numeric, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from decimal import Decimal
import random

import click # Prompts users to enter their information

from datetime import datetime


# Setup Database
#engine = create_engine("postgresql://Campospa:2883@localhost/Bank Account")
engine = create_engine("sqlite:///demo.db")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# Define a class for transactions
class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    type = Column(String)
    amount = Column(Float)
    account_number = Column(Integer)
    timestamp = Column(String, default=datetime.utcnow)
    

    account = relationship("Account", back_populates="transactions")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    user_name = Column(String, unique=True)
    password = Column(String)
    account_number = Column(Integer)
    account_id = Column(Integer, ForeignKey('accounts.id'))

    account = relationship("Account", back_populates="users")

    def __repr__(self):
        return f"<User(name={self.name}, email={self.email}, user_name={self.user_name})>"

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    account_name = Column(String)
    balance = Column(Float, default=0.0)
    account_number = Column(Integer, unique=True)
    
    users = relationship("User", back_populates="account")
    transactions = relationship("Transaction", back_populates="account")

    def __repr__(self):
        return f"<Account(id={self.id}, balance={self.balance}, account_name={self.account_name})>"

# Create tables
Base.metadata.create_all(engine)



class Banking:
    
    @staticmethod
    def create_account(account_name , initial_balance, account_number):
        accounts = Account(account_name=account_name, balance=initial_balance, account_number=account_number)
        session = Session()
        session.add(accounts)
        session.commit()
        print(f"Added {account_name} account with balance {initial_balance}!")
        return account_number

    
    @staticmethod
    def create_user(name, email, user_name, password, account_number):
        session = Session()
        account = session.query(Account).filter_by(account_number=account_number).first()
        if account:
            user = User(name=name, email=email, user_name=user_name, password=password, account_number=account_number)
            session.add(user)
            session.commit()
            print("New user successfully created!")
        else:
            print(f"Account with number {account_number} not found.")
        

    # Make deposits 
    @staticmethod
    def deposit_funds(account_number, amount):
        session = Session()
        account = session.query(Account).filter_by(account_number=account_number).first()
        if account:
            account.balance += amount
            session.commit()
            # Record transaction (Test)
            new_transaction = Transaction(account_id=account.id, account_number=account_number, type='deposit', amount=amount)
            session.add(new_transaction)
            session.commit()
            print(f"Deposit of {amount} received for account {account_number}!")
        else:
            print(f"Account with id {account_number} not found.")

    # Make a withdral
    @staticmethod
    def withdraw_funds(account_number, amount):
        session = Session()
        account = session.query(Account).filter_by(account_name=account_number).first()
        if not account:
            print(f"Account with name {account_number} not found.")
            return
        #amount = Decimal(amount) # convert amountto decimal to match the 'Numeric' data type in the 'balance'. Numeric = decimal in Python
        if amount < 0.0:
            print("Withdrawal amount must be positive.")
        elif amount > account.balance:
            print("Insufficient funds.")
            return
        else:
            try:
                account.balance -= amount
                print(f"You are withdrawing ${amount:.2f} from your account.")
                # Record transaction
                new_transaction = Transaction(account_id=account.id,account_number=account_number,type='withdrawal', amount=amount) #amount=float(amount))
                session.add(new_transaction)
                session.commit()
                print("Withdrawal successful.")
            except Exception as e:
                print("Error occurred during withdrawal transaction recording:", e)

    # Create a method to check available balance given the account number
    def check_balance(account_number):
        session = Session()
        account = session.query(Account).filter_by(account_number=account_number).first()
        if account:
            print(f"Account balance for account {account.account_name}: {account.balance}")
        else:
            print(f"Account with number {account_number} not found.")

# Create a Command Line Interface CLI
@click.group()
def cli():
    pass

# Command to create an account
@click.command(help='Create an account')
@click.option('--account_name', prompt=True)
@click.option('--initial_balance', prompt=True)
def create_account(account_name, initial_balance):
    account_number = generate_account_number()
    Banking.create_account(account_name, float(initial_balance), account_number)
    click.echo(f'Account created with Account Number: {account_number}')

    if click.confirm('Create an user for this account:'):
        create_user(account_number)

def generate_account_number():
    return str(random.randint(10000000000, 99999999999))

# Command to create user
def create_user(account_number):
    name = click.prompt('Enter your name')
    email = click.prompt('Enter your email')
    user_name = click.prompt('Enter your username')
    password = click.prompt('Enter your password')
    Banking.create_user(name, email, user_name, password, account_number)


# Command to deposit funds
@click.command(help="Deposit Funds")
@click.option('--account_number', prompt=True, type=str)
@click.option('--amount', prompt=True, type=float)
def deposit_funds(account_number, amount):
    Banking.deposit_funds(account_number, amount)

# command to withdraw funds
@click.command(help="Withdraw Funds")
@click.option('--account_number', prompt=True, type=str)
@click.option('--amount', prompt=True, type=float)
def withdraw_funds(account_number, amount):
    Banking.withdraw_funds(account_number, amount)

# command to check balance
@click.command(help="Check availble balance")
@click.option('--account_number', prompt=True, type=int)
def check_balance(account_number):
    Banking.check_balance(account_number)


# Clears all tables from the database
@click.command(help="Drop all tables in the database") # Ebnables the user to delete the information in the tables
def clear_database():
    Base.metadata.drop_all(engine)
    print("Database cleared!")


# Execute commands
cli.add_command(create_account)  # These are the commands available for the user
cli.add_command(deposit_funds)
cli.add_command(withdraw_funds)
cli.add_command(check_balance)
cli.add_command(clear_database)


if __name__ == '__main__':
    cli()


