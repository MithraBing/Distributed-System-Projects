"""
CPSC 5520, Seattle University
This is free and unencumbered software released into the public domain.
:Authors: Srimithra Bingi
:Version: 1.0
"""
import pickle
import socket
import sys

BUF_SZ = 1024  # tcp receive buffer size

class Lab1(object):

    def __init__(self, gcd_host, gcd_port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((gcd_host, gcd_port))
        self.member_list = []

    def join_group(self):
        join_message = 'JOIN'
        self.member_list = self.message(self.s, join_message, BUF_SZ)

    def meet_members(self):
        for member_dictionary in self.member_list:
            key, value = member_dictionary['host'], member_dictionary['port']
            member_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            member_socket.connect(key, value)
            member_message = 'HELLO'
            member_pickle = self.message(member_socket, member_message, BUF_SZ)
            print(member_pickle)

    @staticmethod
    def message(sock, send_data, BUF_SZ):
        pickled_message =  pickle.dumps(send_data)
        socket.send(pickled_message)
        carrier = socket.recv(BUF_SZ)
        unpickled_message = pickle.loads(carrier)
        return unpickled_message

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python member.py PORT")
        exit(1)
    host, port = sys.argv[1:]
    lab1 = Lab1(host, int(port))
    lab1.join_group()
    lab1.meet_members()
