'''Implement OOP principles to the app.py file'''

'''Imports and Database implementation'''
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Numeric, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from decimal import Decimal

import click # Prompts users to enter their information

from datetime import datetime


# Setup Database
engine = create_engine("postgresql://Campospa:2883@localhost/Bank Account")
#engine = create_engine("sqlite:///demo.db")
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
    timestamp = Column(String, default=datetime.utcnow)
    

    account = relationship("Account", back_populates="transactions")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    user_name = Column(String, unique=True)
    password = Column(String)
    account_id = Column(Integer, ForeignKey('accounts.id'))

    account = relationship("Account", back_populates="users")

    def __repr__(self):
        return f"<User(name={self.name}, email={self.email}, user_name={self.user_name})>"

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    account_name = Column(String)
    balance = Column(Float, default=0.0)
    
    

    users = relationship("User", back_populates="account")
    transactions = relationship("Transaction", back_populates="account")

    def __repr__(self):
        return f"<Account(id={self.id}, balance={self.balance}, account_name={self.account_name})>"

# Create tables
Base.metadata.create_all(engine)

'''Here we create classes and methods  for Users and Accounts'''

class Banking:
    
    @staticmethod
    def create_account(account_name , initial_balance):
        accounts = Account(account_name=account_name, balance=initial_balance)
        #with Session(engine) as session:
        session = Session()
        session.add(accounts)
        session.commit()
        print(f"Added {account_name} account with balance {initial_balance}!")

    
    @staticmethod
    def create_user(name, email, user_name, password):
        users = User(name=name, email=email, user_name=user_name, password=password)
        session = Session()
        session.add(users)
        session.commit()
        print(f"New user successfully created!")

    # Make deposits 
    @staticmethod
    def make_deposit(account_name, amount):
        session = Session()
        account = session.query(Account).filter_by(account_name=account_name).first()
        if account:
            account.balance += amount
            session.commit()
            # Record transaction (Test)
            new_transaction = Transaction(account_id=account.id,type='deposit', amount=amount)
            session.add(new_transaction)
            session.commit()
            print(f"Deposit of {amount} received for account {account_name}!")
        else:
            print(f"Account with id {account_name} not found.")

    # Make a withdral
    @staticmethod
    def withdraw_funds(account_name, amount):
        session = Session()
        account = session.query(Account).filter_by(account_name=account_name).first()
        if not account:
            print(f"Account with name {account_name} not found.")
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
                new_transaction = Transaction(account_id=account.id,type='withdrawal', amount=amount) #amount=float(amount))
                session.add(new_transaction)
                session.commit()
                print("Withdrawal successful.")
            except Exception as e:
                print("Error occurred during withdrawal transaction recording:", e)

# Create a Command Line Interface CLI
@click.group()
def cli():
    pass

# Command to create an account
@click.command(help='Create an account')
@click.option('--account_name', prompt=True)
@click.option('--initial_balance', prompt=True)
def create_account(account_name, initial_balance):
    Banking.create_account(account_name, initial_balance)

# Command to create user
@click.command(help='Create new user')
@click.option('--name', prompt=True)
@click.option('--email', prompt=True)
@click.option('--user_name', prompt=True)
@click.option('--password', prompt=True)
def create_user(name, email, user_name, password):
    Banking.create_user(name, email, user_name, password)

# Command to deposit funds
@click.command(help="Deposit Funds")
@click.option('--account_name', prompt=True, type=str)
@click.option('--amount', prompt=True, type=float)
def make_deposit(account_name, amount):
    Banking.make_deposit(account_name, amount)

# command to withdraw funds
@click.command(help="Withdraw Funds")
@click.option('--account_name', prompt=True, type=str)
@click.option('--amount', prompt=True, type=float)
def withdraw_funds(account_name, amount):
    Banking.withdraw_funds(account_name, amount)


# Clears all tables from the database
@click.command(help="Drop all tables in the database") # Ebnables the user to delete the information in the tables
def clear_database():
    Base.metadata.drop_all(engine)
    print("Database cleared!")


# Execute commands
cli.add_command(create_account)  # These are the commands available for the user
cli.add_command(create_user)
cli.add_command(make_deposit)
cli.add_command(withdraw_funds)
cli.add_command(clear_database)


if __name__ == '__main__':
    cli()


