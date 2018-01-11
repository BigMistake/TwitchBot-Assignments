import cfg
import socket
import time
import re
import random

# Pattern for all channel messages.
CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
# Get the name of the channel host
host = cfg.CHAN.replace("#", "")
# Let's keep track of the statuses ("active","inactive"), starting with inactive.
status = "inactive"
# What is the chosen type?
atype = ""
# Name of the chosen type?
chosen = ""
# Assignment types and their categories.
WHAT = ["Melee", "Crossbow", "Shotgun", "SMG", "Assault", "Sniper", "Throwable", "Vehicle", "5.56", "7.62", "9mm",
        ".300", ".45"]
HOW = ["Running", "Honking", "Stunt Mode", "Open Mic", "Non-Lethal"]
# Keep track of the users that voted
voters = []
# Keep track of the options and their votes
votes = {}
highvote = 0
votedoption = ""

def chatChannel(msg):
    full_msg = "PRIVMSG {} :{}\r\n".format(cfg.CHAN, msg)
    msg_encoded = full_msg.encode("utf-8")
    s.send(msg_encoded)


def chatUser(user,msg):
    full_msg = "PRIVMSG {} :{}\r\n".format(user, msg)
    msg_encoded = full_msg.encode("utf-8")
    s.send(msg_encoded)
    print(full_msg)


def start():
    global status
    global atype
    global chosen

    status = "active"
    toss = random.randint(0, 1)
    # Flip a coin and see what assignment type we get.
    if toss == 0:
        atype = WHAT
        chosen = "WHAT"
    else:
        atype = HOW
        chosen = "HOW"

    chatChannel("The host has started Assignment Time! Looks like we'll be doing a " + chosen +
         " assignment, the choices are:\n")
    for choice in atype:
        chatChannel(choice + "\n")
        votes[choice] = 0
    chatChannel("You can vote by sending your choice to chat. The host decides when to end the voting.")
    print(atype)


def stop():
    global votes
    global voters
    global status
    global atype
    global chosen
    global votedoption
    global highvote

    print(votes)
    print(voters)

    chatChannel("Voting has ended and the results are in:")

    for key, value in votes.items():
        chatChannel(key + ": " + str(value))
        if value > highvote:
            highvote = value
            votedoption = key

    if highvote == 0:
        chatChannel("No one has voted. Better luck next time!")
    else:
        chatChannel(votedoption + " has won. Thanks for voting, and good luck to your host!")

    status = "inactive"
    atype = ""
    chosen = ""
    voters = []
    votes = {}
    highvote = 0
    votedoption = ""


# Network functions.
s = socket.socket()
s.connect((cfg.HOST, cfg.PORT))
s.send("PASS {} \r\n".format(cfg.PASS).encode("utf-8"))
s.send("NICK {} \r\n".format(cfg.NICK).encode("utf-8"))
s.send("JOIN {} \r\n".format(cfg.CHAN).encode("utf-8"))


# Main loop
while True:
    response = s.recv(1024).decode("utf-8")
    # Sometimes Twitch sends a PING asking if we're active. To not get disconnected we need to respond with a PONG.
    if response == "PING :tmi.twitch.tv\r\n":
        s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
    # Anything else is a message sent by a user
    else:
        username = re.search(r"\w+", response).group(0)  # return the entire match
        message = CHAT_MSG.sub("", response)
        print("'" + message.rstrip("\r\n") + "'")

        if username == host and "!assignment start" in message:
            start()

        if message.rstrip("\r\n") in atype:
            choice = message.rstrip("\r\n")
            print("Voted!")
            if username not in voters:
                votes[choice] += 1
                voters.append(username)

        if username == host and "!assignment stop" in message:
            stop()

    time.sleep(1/cfg.RATE)
