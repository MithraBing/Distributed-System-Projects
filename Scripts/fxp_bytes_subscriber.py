"""
CPSC 5520, Seattle University
This is free and unencumbered software released into the public domain.
:Authors: Srimithra Bingi
:Version: 1.0
"""

import ipaddress

from array import array
from datetime import datetime

def deserialize_rate(byte_rate):
    """
    Used to deserialize the rate bytes.
    """

    rate_array = array('d')
    rate_array.frombytes(byte_rate)
    return rate_array[0]

def serialize_address(address):

    """
    Used to Serialiize the rate bytes.
    """
    
    address_bytes = ipaddress.ip_address(address[0]).packed
    port_bytes = address[1].to_bytes(2, byteorder="big")
    return address_bytes + port_bytes

def deserialize_utcdatetime(time_stamp):

    """
    Used to deserialize the time_stamp bytes.
    """
    time_array = array('L')
    time_array.frombytes(time_stamp)
    time_array.byteswap()
    time = datetime.fromtimestamp(time_array[0] / 1_000_000)
    return time + (datetime.utcnow() - datetime.now())

def demarshal_message(byte_message):

    """
    Utilises other functions written above to demarshel the message and returns the quotes in the message.
    """
    quote_count = int(len(byte_message) / 32)
    quotes = []
    for x in range(0, quote_count):
        quote_bytes = byte_message[x * 32 : x * 32 + 32]
        quote = {}
        quote['timestamp'] = deserialize_utcdatetime(quote_bytes[0:8])
        quote['currency'] = quote_bytes[8:11].decode("utf-8") + "/" + quote_bytes[11:14].decode("utf-8")
        quote['rate'] = deserialize_rate(quote_bytes[14:22])
        quotes.append(quote)
    return quotes