"""
CPSC 5520, Seattle University
This is free and unencumbered software released into the public domain.
:Authors: Srimithra Bingi
:Version: 1.0
"""
import pickle
import socket
import sys

BUF_SZ = 1024  # buffer size for the tcp receive


class Lab1(object):

    """
    This class is for connecting to a Group Coordinator Daemon (GCD), getting a lit of members from it and
    then connect to each member in the list, then send it a message followed by receiving a message from it.
    """

    # Initializing the socket and connect to the GCD

    def __init__(self, gcd_host, gcd_port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((gcd_host, gcd_port))
        self.member_list = []

    # Sending the JOIN message to the GCD and storing the members list

    def join_group(self):
        gcd_message = "JOIN"
        self.member_list = self.message(self.s, gcd_message, BUF_SZ)
        self.s.close()

    # Connecting to other members, sending and receiving the message (through the message method) from them

    def meet_members(self):
        for member_dictionary in self.member_list:
            key, value = member_dictionary["host"], member_dictionary["port"]
            prompt_message = "HELLO to {'host': '" + str(key) + "', 'port': " + str(value) + "}"
            print(prompt_message)
            try:
                member_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                member_socket.connect((key, value))
                member_socket.settimeout(1500)
                member_message = "HELLO"
                member_pickle = self.message(member_socket, member_message, BUF_SZ)
                print(member_pickle)
                member_socket.close()
            except Exception as failure:
                print("Failed to connect:", failure)

    # Static method to pickle the message, send it and then load the reply

    @staticmethod
    def message(sock, send_data, buf_sz):
        pickled_message = pickle.dumps(send_data)
        sock.sendall(pickled_message)
        carrier = sock.recv(buf_sz)
        reply_message = pickle.loads(carrier)
        return reply_message


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python member.py PORT")
        exit(1)
    host, port = sys.argv[1:]
    lab1 = Lab1(host, int(port))
    join_message = "JOIN ('" + host + "', " + port + ")"
    print(join_message)
    lab1.join_group()
    lab1.meet_members()
