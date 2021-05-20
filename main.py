import random
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()


def check_luhn(card_num):
    num = [int(i) for i in card_num]
    nSum = 0
    isSecond = False
    for i in range(15, -1, -1):
        if isSecond is True:
            num[i] *= 2
        nSum += num[i] // 10
        nSum += num[i] % 10
        isSecond = not isSecond
    if nSum % 10 == 0:
        return True
    else:
        return False


class Account:
    def __init__(self):
        self.number = ""
        self.PIN = ""
        self.balance = 0

    def account_num_create(self):
        IIN = "400000"
        account_id = ""
        for _ in range(9):
            account_id += str(random.randint(0, 9))
        temp = IIN + account_id
        nums = list()
        for i in range(15):
            nums.append(int(temp[i]))
        for i in range(0, 15, 2):
            nums[i] *= 2
        for i in range(15):
            if nums[i] > 9:
                nums[i] -= 9
        for checksum in range(10):
            if (sum(nums) + checksum) % 10 == 0:
                break
            checksum += 1
        self.number = IIN + account_id + str(checksum)
        return self.number

    def PIN_create(self):
        for _ in range(4):
            self.PIN += str(random.randint(0, 9))
        return self.PIN


accounts = {}
cur.execute('''CREATE TABLE IF NOT EXISTS 
            card(
            id integer,
            number text,
            pin text,
            balance integer default 0)''')
while True:
    menu = int(input("1. Create an account \n2. Log into account\n0. Exit\n"))
    if menu == 1:
        account = Account()
        card_number = account.account_num_create()
        PIN = account.PIN_create()
        print("Your card has been created\nYour card number:\n{}\nYour card PIN:\n{}".format(card_number, PIN))
        accounts[card_number] = PIN
        cur.execute("SELECT id FROM card")
        seq = cur.fetchall()
        if seq is None:
            primary_key_id = 1
        else:
            primary_key_id = len(seq) + 1
        cur.execute(f'''INSERT INTO card (id, number, pin) VALUES ({primary_key_id}, {card_number}, {PIN})''')
        conn.commit()
        primary_key_id += 1
    elif menu == 2:
        card_number_input = input("Enter your card number:\n")
        PIN_input = input("Enter your PIN:\n")
        cur.execute(f'''
        SELECT 
            number, 
            pin, 
            balance 
        FROM
            card 
        WHERE number = {card_number_input} AND pin = {PIN_input}''')
        acc = cur.fetchone()
        if acc is not None:
            print("You have successfully logged in!")
            while True:
                menu_2 = int(input("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n"))
                if menu_2 == 1:
                    cur.execute(f"SELECT balance FROM card WHERE number = {card_number_input}")
                    balance = cur.fetchone()
                    print("Balance: {}".format(balance))
                elif menu_2 == 2:
                    income = int(input("Enter income: "))
                    cur.execute(f"SELECT balance FROM card WHERE number = {card_number_input}")
                    balance = cur.fetchone()
                    cur.execute(f"UPDATE card SET balance = {balance + income} WHERE number = {card_number_input}")
                    conn.commit()
                    print("Income was added!")
                elif menu_2 == 3:
                    print("Transfer")
                    card_num_transfer = input("Enter card number: ")
                    check = check_luhn(card_num_transfer)
                    if check is False:
                        print("Probably you made a mistake in the card number. Please try again!")
                    else:
                        cur.execute(f"SELECT number FROM card WHERE number = {card_num_transfer}")
                        card_num_transfer = cur.fetchone()
                        if card_num_transfer is None:
                            print("Such a card does not exist.")
                        elif card_num_transfer == acc[0]:
                            print("You can't transfer money to the same account!")
                        else:
                            amount = int(input("Enter how much money you want to transfer:"))
                            if amount <= acc[2]:
                                cur.execute(f"SELECT balance FROM card WHERE number = {card_num_transfer}")
                                balance_1 = cur.fetchone()
                                cur.execute(f"UPDATE card SET balance = {balance + amount} WHERE number "
                                            f"= {card_num_transfer}")
                                cur.execute(f"SELECT balance FROM card WHERE number = {card_number_input}")
                                balance_2 = cur.fetchone()
                                cur.execute(f"UPDATE card SET balance = {balance - amount} WHERE number "
                                            f"= {card_number_input}")
                                conn.commit()
                                print("Success!")
                            else:
                                print("Not enough money!")
                elif menu_2 == 4:
                    cur.execute(f"DELETE FROM card WHERE number = {card_number_input}")
                    conn.commit()
                    print("The account has been closed!")
                elif menu_2 == 5:
                    print("You have successfully logged out!")
                else:
                    menu = 0
                    break
        else:
            print("Wrong card number or PIN!")
    if menu == 0:
        print("Bye!")
        break
