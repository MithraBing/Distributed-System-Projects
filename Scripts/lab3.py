"""
CPSC 5520, Seattle University
This is free and unencumbered software released into the public domain.
:Authors: Srimithra Bingi
:Version: 1.0
"""

import socket
import sys
import time
import threading
import math
import fxp_bytes
import fxp_bytes_subscriber as sub

from datetime import datetime, timedelta
from bellman_ford import Bellman

LISTENER_ADDRESS = (socket.gethostbyname(socket.gethostname()), 12345)

class Lab3(object):

    """
    Initialising Lab3
    """

    def __init__(self, PROVIDER_ADDRESS):

        self.provider_address = PROVIDER_ADDRESS
        self.graph = {}

    """
    Creating socket and listening for quotes. Demarsheling messages using the demarshel_message function in
    fxp_bytes_subscriber. Running Bellman_ford to identify negative cycles.
    """

    def listen(self):

        listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener.bind(LISTENER_ADDRESS)
        listen_time = datetime.now() + (datetime.utcnow() - datetime.now())

        while True:

            message = listener.recv(1024)
            demarshalled_message = sub.demarshal_message(message)

            for quote in demarshalled_message:

                time_diff = (listen_time - quote['timestamp']).total_seconds()

                if time_diff < 0.1:

                    currency = quote['currency'].split('/')
                    print(str(datetime.now())+" : ", "{} {} {}".format(currency[0], currency[1], quote['rate']))
                    self.new_graph(quote, currency)
                    listen_time = quote['timestamp']

                else:
                    print('Ignoring out-of-sequence message')
                
            self.clean_stale()
            bellman = Bellman(self.graph)
            distance, previous, negative_edge = bellman.shortest_path('USD', 1e-12)
            if not negative_edge is None:
                self.arbitrage(previous, 'USD')
    
    def clean_stale(self):

        """
        Cleaning stale quotes in graph
        """

        stale_time = datetime.now() - timedelta(seconds = 1.5)
        stale_count = 0

        for currency1 in self.graph:
            for currency2 in self.graph[currency1]:
                if self.graph[currency1][currency2]['timestamp'] <= stale_time:
                    del self.graph[currency1][currency2]
                    print('Removed stale quote for ({},{})'.format(currency1, currency2))

    def new_graph(self, quote, currency):

        """
        Updating graph with new quotes' nodes and edges.
        """

        rate = -1 * math.log(quote['rate'])
        if not currency[0] in self.graph:
            self.graph[currency[0]] = {}

        self.graph[currency[0]][currency[1]] = {'timestamp': quote['timestamp'], 'rate': rate}

        if not currency[1] in self.graph:
            self.graph[currency[1]] = {}

        self.graph[currency[1]][currency[0]] = {'timestamp': quote['timestamp'], 'rate': -1 * rate}
                    

    def arbitrage(self, previous, start):

        """
        Printing out the details of Abritrage cycles.
        """

        step_list = [start]
        step_prev = previous[start]
        trade_amount = 100
        last = start


        while not step_prev == start:
            step_list.append(step_prev)
            step_prev = previous[step_prev]
        
        step_list.append(start)
        step_list.reverse()
        
        print("start with {} 100".format(start))
		
        trade_value = trade_amount

        for i in range(1, len(step_list)):
            currency = step_list[i]
            rate = math.exp(-1 * self.graph[last][currency]['rate'])
            trade_value *= rate
            print("Exchange {} for {} at {} --> {} {}".format(last, currency, rate, currency, trade_value))
            last = currency
			
        profit = trade_value - trade_amount
        print(" --> Profit of {} {}".format(profit, start))

    def subscribe(self):

        """
        Initialising a socket to send the listener address and port to forex_provider.
        """

        while True:
            print("Subscribing to {}".format(self.provider_address))

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                serialized_address = sub.serialize_address(LISTENER_ADDRESS)
                sock.sendto(serialized_address, self.provider_address)
                sock.close()
                
            time.sleep(600)
		
    def run(self):

        """
        Using threads to run listener and subscriber in order,
        """

        listener_thread = threading.Thread(target = self.listen)
        listener_thread.start()
        subscriber_thread = threading.Thread(target = self.subscribe)
        subscriber_thread.start()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python lab3.py provider_host provider_port")
        exit(1)
            
    address = (sys.argv[1], int(sys.argv[2]))
    subs  = Lab3(address)
    subs.run()