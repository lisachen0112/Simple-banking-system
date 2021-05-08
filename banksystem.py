import random
import _sqlite3

conn = _sqlite3.connect("card.s3db")
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS card")
cur.execute("CREATE TABLE IF NOT EXISTS card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)")
conn.commit()

def delete_account():
    cur.execute("DELETE FROM card WHERE number = ?", (str(card_input),))
    print("\nThe account has been closed!\n")

def add_income():
    add_income = int(input("Enter income: "))
    query = cur.execute("SELECT number, pin, balance FROM card WHERE number = ?", (str(card_input),)).fetchall()
    new_amount = query[0][2] + add_income
    cur.execute("UPDATE card SET balance = ? WHERE number = ?", (new_amount, str(card_input)))
    conn.commit()
    print("Income was added!\n")

def luhn_algorithm(BIN_account):
    list_BIN_account = list(BIN_account)
    #Convert to integer
    for i in range(len(list_BIN_account)):
        list_BIN_account[i] = int(list_BIN_account[i])

    #Multiply odd positions by 2
    for i in range(len(list_BIN_account)):
        if i%2 == 0 or i == 0:
            list_BIN_account[i] *= 2

    #Subtract 9
    for i in range(len(list_BIN_account)):
        if list_BIN_account[i] > 9:
            list_BIN_account[i] -= 9

    #Sum all numbers
    global checksum
    checksum = sum(list_BIN_account)

def create_account():
    cards_query = cur.execute("SELECT number FROM card").fetchall()
    account_list = []
    for i in range(len(cards_query)):
        account_list.append(cards_query[i][0][6:-1])
    account_identifier = ''.join(str(random.randint(0,9)) for _ in range(9))
    while account_identifier in account_list:
        account_identifier = ''.join(str(random.randint(0,9)) for _ in range(9))
    else:
        account_list.append(account_identifier)
        BIN_acc = "400000" + account_identifier

        luhn_algorithm(BIN_acc)

        #Checksum + last digit
        if checksum % 10 == 0:
            account_number = BIN_acc + "0"
        else:
            last_digit = str(10 - (checksum % 10))
            account_number = BIN_acc + last_digit

    PIN = ''.join(str(random.randint(0,9)) for _ in range(4))
    cur.execute("INSERT INTO card (number, pin) VALUES (?, ?)", (account_number, PIN))
    conn.commit()
    print("\nYour card has been created\nYour card number:\n{}\nYour card PIN:\n{}\n".format(account_number, PIN))



def bank():
    test = 1
    while test:
        home = input("1. Create an account\n2. Log into account\n0. Exit\n")
        #Create  an account
        if home == "1":
            create_account()

        #Log in
        elif home == "2":
            global card_input, PIN_input
            card_input = int(input("\nEnter your card number:\n"))
            PIN_input = input("Enter your PIN:\n")
            global query
            query = cur.execute("SELECT number, pin, balance FROM card WHERE number = ?", (str(card_input),)).fetchall()
            if not query or query[0][1] != PIN_input:
                print("\nWrong card number or PIN!\n")
            else:
                print("\nYou have successfully logged in!\n")
                while True:
                    balance = int(input("""1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit\n"""))
                    if balance == 1:
                        balance = cur.execute("SELECT number, pin, balance FROM card WHERE number = ?", (str(card_input),)).fetchall()
                        print(f"Balance: {balance[0][2]}\n")
                    elif balance == 2:
                        add_income()
                    elif balance == 3:
                        print("Transfer")
                        recipient = input("Enter card number:\n")
                        last_digit = int(recipient[-1:])
                        for_checksum = recipient[:-1]
                        luhn_algorithm(for_checksum)
                        recipient_query = cur.execute("SELECT number, pin, balance FROM card WHERE number = ?", (str(recipient),)).fetchall()
                        if (checksum + last_digit) % 10 != 0:
                            print("Probably you made a mistake in the card number. Please try again!\n")
                        elif recipient == str(card_input):
                            print("You can't transfer money to the same account!")
                        elif not recipient_query:
                            print("Such a card does not exist.")
                        else:
                            transfer = int(input("Enter how much money you want to transfer:"))
                            query = cur.execute("SELECT number, pin, balance FROM card WHERE number = ?", (str(card_input),)).fetchall()
                            if transfer > query[0][2]:
                                print("Not enough money!")
                            else:
                                amount_in_balance = cur.execute("SELECT number, pin, balance FROM card WHERE number = ?", (str(card_input),)).fetchall()
                                after_transfer = amount_in_balance[0][2] - transfer
                                cur.execute("UPDATE card SET balance = ? WHERE number = ?", (after_transfer, str(card_input)))
                                conn.commit()
                                recipient_balance =  cur.execute("SELECT number, pin, balance FROM card WHERE number = ?", (recipient,)).fetchall()
                                recipient_after_transfer = recipient_balance[0][2] + transfer
                                cur.execute("UPDATE card SET balance = ? WHERE number = ?", (recipient_after_transfer, recipient))
                                conn.commit()
                                print("Success!")
                    elif balance == 4:
                        delete_account()
                        conn.commit()
                        break
                    elif balance == 5:
                        print("\nYou have successfully logged out!")
                        break
                    else:
                        print("\nBye!")
                        test = 0
                        break
        #Exit
        else:
            print("\nBye!")
            break
bank()