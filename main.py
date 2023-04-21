from state import *
from game import *
from agent import *
import time
from email.message import EmailMessage
import smtplib
import ssl

PASSWORD = "qpjibgcsiflcjrmq"

def choice(lst):
    length = len(lst)
    if length == 0:
        return None
    if length == 1:
        return 0

    for i in range(length):
        print(f"{i}: {lst[i]}")
    while True:
        c = input(f"Please enter a number in the range 0 to {length-1}: ")
        if c.isdigit():
            if int(c) in range(length):
                return int(c)
        print(f"Please enter a number in the range 0 to {length-1}.")

def info():
    print("Welcome to Coup!")
    print("Please refrain from observing the code at least until after completing the playthrough.")
    print("By continuing, you are agreeing for your game data to be collected.")
    c = choice(["Consent and continue.", "Quit."])
    if c == 1:
        quit()
    print("Please confirm you have not inspected the code and are unaware of the strategies your opponents will implement.")
    c = choice(["I confirm", "I can no longer participate in this experiment"])
    if c == 1:
        quit()
    print("Before beginning, please carefully read the rules of Coup and refer to them throughout play: https://www.ultraboardgames.com/coup/game-rules.php")
    press_to_continue()
    name = input("Please enter your full name: ")
    email = input("Please enter your email if you wish to receive a copy of the data saved. You will be sent a test email to verify it works which you can discard.\nEnsure email entered is valid or input nothing and simply press ENTER to continue: ")
    print("Please enter your experience with Coup:")
    xp = choice(["First time playing.", "Played before a few times.", "Have played fairly regularly before.", "I have played Coup a lot.", "I consider myself very skilled at Coup."])
    print("You will be playing 3 games of Coup as 'Player 0' against two computer players.")
    print("This will take around 10-20 minutes. Please DO NOT close the program until told to do so. Good luck!")
    press_to_continue()
    return name, email, xp

def send_results(data, cc = None):
    sender = "coupresults@gmail.com"
    receiver = []
    receiver.append("coupresults@gmail.com")
    if cc:
        receiver.append(cc)
    subject = "Test email"
    body = data

    em = EmailMessage()
    em["From"] = sender
    em["To"] = receiver
    em["Subject"] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(sender, PASSWORD)
        return smtp.sendmail(sender, receiver, em.as_string())

def main():
    name, email, xp = info()
    sent = send_results(f"Test email for {name}. Please feel free to delete.", cc = email)
    if sent != {}:
        raise Exception("Test email could not be sent so results will not get through. Please contact sc20tc@leeds.ac.uk for advice.")
    num_players = 3
    iterations = 3
    results = [-1, -1, -1]
    states = [State(num_players=num_players, agents={0:"human"}),
            State(num_players=num_players, agents={0:"human",1:"random_no_bluff",2:"random_no_bluff"}),
            State(num_players=num_players, agents={0:"human",1:"random_bluff_bias",2:"random_bluff_bias"})]

    t_start = time.process_time()
    for i in range(iterations):
        print(f"Game {i+1}!\n")
        state = states[i]
        while not state.is_winner():
            state.transition_old()
        winner = state.get_winner().id
        results[i] = winner
        print(f"Player {winner} wins the game!")
    t_elapsed = time.process_time() - t_start
    s1 = f"Name: {name}."
    s2 = f"Experience level: {xp}."
    s3 = f"Game 1 winner (against 2 random agents): {results[0]}."
    s4 = f"Game 2 winner (against 2 agents which never bluffed): {results[1]}."
    s5 = f"Game 3 winner (against 2 agents which bluffed 30% of the time): {results[2]}."
    s6 = f"Time elapsed: {t_elapsed}."
    data = f"{s1}\n{s2}\n{s3}\n{s4}\n{s5}\n{s6}"
    send_results(data, cc = email)
    print("\n\n")
    print(data)
    print("Thank you very much for your time! I hope you enjoyed playing.\n\n")
    print("You may now close the application.")

if __name__ == "__main__":
    main()