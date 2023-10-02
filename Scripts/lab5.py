"""
CPSC 5520, Seattle University
This is free and unencumbered software released into the public domain.
:Author: Srimithra Bingi
:Version: 1.0
"""
import sys
import time
import socket
import hashlib

client_host, client_port = '127.0.0.1', 59550
bit_host, bit_port = '92.84.145.94', 8333
msg_header_sz = 24

class Lab(object):

    def compactsize_t(n):
        if n < 252:
            return Lab.uint8_t(n)
        if n < 0xffff:
            return uint8_t(0xfd) + Lab.uint16_t(n)
        if n < 0xffffffff:
            return uint8_t(0xfe) + Lab.uint32_t(n)
        return Lab.uint8_t(0xff) + Lab.uint64_t(n)


    def unmarshal_compactsize(b):
        key = b[0]
        if key == 0xff:
            return b[0:9], Lab.unmarshal_uint(b[1:9])
        if key == 0xfe:
            return b[0:5], Lab.unmarshal_uint(b[1:5])
        if key == 0xfd:
            return b[0:3], Lab.unmarshal_uint(b[1:3])
        return b[0:1], Lab.unmarshal_uint(b[0:1])


    def bool_t(flag):
        return Lab.uint8_t(1 if flag else 0)


    def ipv6_from_ipv4(ipv4_str):
        pchIPv4 = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xff, 0xff])
        return pchIPv4 + bytearray((int(x) for x in ipv4_str.split('.')))


    def ipv6_to_ipv4(ipv6):
        return '.'.join([str(b) for b in ipv6[12:]])


    def uint8_t(n):
        return int(n).to_bytes(1, byteorder='little', signed=False)


    def uint16_t(n):
        return int(n).to_bytes(2, byteorder='little', signed=False)


    def int32_t(n):
        return int(n).to_bytes(4, byteorder='little', signed=True)


    def uint32_t(n):
        return int(n).to_bytes(4, byteorder='little', signed=False)


    def int64_t(n):
        return int(n).to_bytes(8, byteorder='little', signed=True)


    def uint64_t(n):
        return int(n).to_bytes(8, byteorder='little', signed=False)


    def unmarshal_int(b):
        return int.from_bytes(b, byteorder='little', signed=True)


    def unmarshal_uint(b):
        return int.from_bytes(b, byteorder='little', signed=False)


    def print_msg(msg, text=None):
        """
        Report the contents of the given bitcoin message
        :param msg: bitcoin message including header
        :return: message type
        """
        print('\n{}MESSAGE'.format('' if text is None else (text + ' ')))
        print('({}) {}'.format(len(msg), msg[:60].hex() + ('' if len(msg) < 60 else '...')))
        payload = msg[msg_header_sz:]
        command = Lab.print_header(msg[:msg_header_sz], Lab.checksum(payload))
        if command == 'version':
            Lab.print_version_msg(payload)
        elif command == 'getblocks':
            Lab.print_get_blocks(payload)


    def print_version_msg(b):
        """
        Report the contents of the given bitcoin version message (sans the header)
        :param payload: version message contents
        """
        # pull out fields
        version, my_services, epoch_time, your_services = b[:4], b[4:12], b[12:20], b[20:28]
        rec_host, rec_port, my_services2, my_host, my_port = b[28:44], b[44:46], b[46:54], b[54:70], b[70:72]
        nonce = b[72:80]
        user_agent_size, uasz = Lab.unmarshal_compactsize(b[80:])
        i = 80 + len(user_agent_size)
        user_agent = b[i:i + uasz]
        i += uasz
        start_height, relay = b[i:i + 4], b[i + 4:i + 5]
        extra = b[i + 5:]

        # print report
        prefix = '  '
        print(prefix + 'VERSION')
        print(prefix + '-' * 56)
        prefix *= 2
        print('{}{:32} version {}'.format(prefix, version.hex(), Lab.unmarshal_int(version)))
        print('{}{:32} my services'.format(prefix, my_services.hex()))
        time_str = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(Lab.unmarshal_int(epoch_time)))
        print('{}{:32} epoch time {}'.format(prefix, epoch_time.hex(), time_str))
        print('{}{:32} your services'.format(prefix, your_services.hex()))
        print('{}{:32} your host {}'.format(prefix, rec_host.hex(), Lab.ipv6_to_ipv4(rec_host)))
        print('{}{:32} your port {}'.format(prefix, rec_port.hex(), Lab.unmarshal_uint(rec_port)))
        print('{}{:32} my services (again)'.format(prefix, my_services2.hex()))
        print('{}{:32} my host {}'.format(prefix, my_host.hex(), Lab.ipv6_to_ipv4(my_host)))
        print('{}{:32} my port {}'.format(prefix, my_port.hex(), Lab.unmarshal_uint(my_port)))
        print('{}{:32} nonce'.format(prefix, nonce.hex()))
        print('{}{:32} user agent size {}'.format(prefix, user_agent_size.hex(), uasz))
        print('{}{:32} user agent \'{}\''.format(prefix, user_agent.hex(), str(user_agent, encoding='utf-8')))
        print('{}{:32} start height {}'.format(prefix, start_height.hex(), Lab.unmarshal_uint(start_height)))
        print('{}{:32} relay {}'.format(prefix, relay.hex(), bytes(relay) != b'\0'))
        if len(extra) > 0:
            print('{}{:32} EXTRA!!'.format(prefix, extra.hex()))


    def print_header(header, expected_cksum=None):
        """
        Report the contents of the given bitcoin message header
        :param header: bitcoin message header (bytes or bytearray)
        :param expected_cksum: the expected checksum for this version message, if known
        :return: message type
        """
        magic, command_hex, payload_size, cksum = header[:4], header[4:16], header[16:20], header[20:]
        command = str(bytearray([b for b in command_hex if b != 0]), encoding='utf-8')
        psz = Lab.unmarshal_uint(payload_size)
        if expected_cksum is None:
            verified = ''
        elif expected_cksum == cksum:
            verified = '(verified)'
        else:
            verified = '(WRONG!! ' + expected_cksum.hex() + ')'
        prefix = '  '
        print(prefix + 'HEADER')
        print(prefix + '-' * 56)
        prefix *= 2
        print('{}{:32} magic'.format(prefix, magic.hex()))
        print('{}{:32} command: {}'.format(prefix, command_hex.hex(), command))
        print('{}{:32} payload size: {}'.format(prefix, payload_size.hex(), psz))
        print('{}{:32} checksum {}'.format(prefix, cksum.hex(), verified))
        return command
    
    def print_get_blocks(payload):
        

        version = payload[:4]
        count =  payload[4:5]
        header_hash = payload[5:37]
        stop = payload[37:]

        prefix = '  '
        print(prefix + 'GETBLOCKS')
        print(prefix + '-' * 56)
        prefix *= 2
        print('{}{:32} version {}'.format(prefix, version.hex(), Lab.unmarshal_int(version)))
        print('{}{:32} hashcount {}'.format(prefix, count.hex(), Lab.unmarshal_compactsize(count)[1]))
        print('{}{:32} header hash'.format(prefix, header_hash.hex()[:32]))
        print('{}{:32} stop hash'.format(prefix, stop.hex()[:32]))
    
    def messasge_header(command, payload=None):
       
        start = bytearray.fromhex('f9beb4d9') 
        if len(command) < 12:
            command += ('\0' * (12 - len(command)))
        command = command.encode()

        if payload is None:
            payload = ''.encode()
        payload_size = Lab.uint32_t(len(payload))
        checks = Lab.checksum(payload)
        header = start + command + payload_size + checks
        return header

    
    def message_version():
       
        version = Lab.int32_t(70015)

        services = Lab.uint64_t(0)

        timestamp = Lab.int64_t(int(time.time()))

        host_services = Lab.uint64_t(1)

        host_ip = Lab.ipv6_from_ipv4(bit_host)

        host_port = Lab.uint16_t(bit_port)

        address_services = services

        address_ip = Lab.ipv6_from_ipv4(client_host)

        address_port = Lab.uint16_t(client_port)

        nonce = Lab.uint64_t(0)

        user_agent_bytes = Lab.compactsize_t(0)

        start = Lab.int32_t(0)

        relay = Lab.bool_t(False)

        version_msg = version + services + timestamp + host_services + \
                      host_ip + host_port + address_services + \
                      address_ip + address_port + nonce + user_agent_bytes + \
                      start + relay

        return version_msg

    def blockhead():

        version = int32_t(4)
        prev_blockhead = bytes.fromhex('000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f')
        merkle_hash = prev_blockhead
        time = uint32_t(int(time.time()))
        nonce = uint32_t(0)
        nbits = uint32_t(0)

        print('Previous Block Header\'s Hash', prev_blockhead)
        blockhead_hash = version + prev_blockhead + merkle_hash + time + nbits \
                            + nonce
        print('Block Header\'s Hash', blockhead_hash, sys.getsizeof(blockhead_hash))
        return blockhead_hash

    def get_block_message():

        core_version = 70015
        bit_hashblock = bytes.fromhex('000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f')
        version = Lab.uint32_t(core_version)
        hashcount = Lab.compactsize_t(1)
        bit_hashblock = bytearray.fromhex(bit_hashblock.hex())
        bit_hashblock.reverse()
        hdr_hashes = bit_hashblock
        stop = bytearray(32)

        return version + hashcount + hdr_hashes + stop
       
    def double_sha256(payload):
        """ Hashes byte object twice with SHA-256, returns hash
        :param b: byte object to be double hashed
        :returns: hashed(b)
        """
        hashed = hashlib.sha256(hashlib.sha256(payload).digest()).digest()
        return hashed
    
    def checksum(payload):

        hashed = hashlib.sha256(hashlib.sha256(payload).digest()).digest()
        return hashed[0:4]
    
        
if __name__ == '__main__':
    print('Running client')
    my_block = 4165706 % 10000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((bit_host, bit_port))
    version_message = Lab.message_version()
    version_header = Lab.messasge_header('version', version_message)
    version = version_header + version_message
    
    Lab.print_msg(version_header + version_message, 'sending')
    s.sendall(version)
    header = s.recv(msg_header_sz)
    payload_size = Lab.unmarshal_uint(header[16:20])
    payload = s.recv(payload_size)

    Lab.print_msg(header + payload, 'received')
    verack = Lab.messasge_header('verack')
    Lab.print_msg(verack, 'sending')
    s.sendall(verack)
    header = s.recv(msg_header_sz)

    Lab.print_msg(header, 'received')
    block_msg = Lab.get_block_message()
    block_hdr = Lab.messasge_header('feelfitter', block_msg)
    block = block_hdr + block_msg

    Lab.print_msg(block, 'sending')
    s.sendall(block_msg)
    header = s.recv(msg_header_sz)
    payload_size = Lab.unmarshal_uint(header[16:20])
    payload = s.recv(payload_size)
    Lab.print_msg(header + payload, 'received')

    Lab.print_msg(block, 'sending')
    s.sendall(block_msg)
    header = s.recv(msg_header_sz)
    payload_size = Lab.unmarshal_uint(header[16:20])
    payload = s.recv(payload_size)
    Lab.print_msg(header + payload, 'received')

    Lab.print_msg(block, 'sending')
    s.sendall(block_msg)
    header = s.recv(msg_header_sz)
    payload_size = Lab.unmarshal_uint(header[16:20])
    payload = s.recv(payload_size)
    Lab.print_msg(header + payload, 'received')




