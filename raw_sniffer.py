import os
import socket
import argparse
import struct

ETH_P_ALL = 0x0003
ETH_SIZE = 14
def make_ethernet_header(raw_data) :
   ether = struct.unpack('!6B6BH', raw_data)

   if ether[12] == 2048 :        #### ip 헤더일경우 
      return {'[dst]':'%02x:%02x:%02x:%02x:%02x:%02x' %ether[:6], 
      '[src]':'%02x:%02x:%02x:%02x:%02x:%02x' %ether[6:12], 
      '[ether_type]':ether[12]}
   else :                        #### ip 헤더가 아닐경우
      return 1

def make_IP_header(raw_data) :
   ip = struct.unpack('!BBHHBBBBH4B4B', raw_data)
   ip_fir = int(ip[0])           ##version, header_length정보

   return{'[version]':'%s' % (ip_fir // 16), 
      '[header_length]':'%s' % (ip_fir % 16),
      '[tos]':'%x' % ip[1],
      '[total_length]':'%d' % ip[2],
      '[id]':'%d' % ip[3],
      '[flag]':'%x' % ip[4],
      '[offset]':'%x' % ip[5],
      '[ttl]':ip[6],
      '[protocal]':ip[7],
      '[checksum]':ip[8],
      '[src]':'%d:%d:%d:%d' % ip[9:13],
      '[dst]':'%d:%d:%d:%d' % ip[13:17]}

def dumpcode(buf):
   print("%7s"% "offset ", end='')
   for i in range(0, 16):
      print("%02x " % i, end='')

      if not (i%16-7):
         print("- ", end='')
         
   print("")

   for i in range(0, len(buf)):
      if not i%16:
         print("0x%04x" % i, end= ' ')

      print("%02x" % buf[i], end= ' ')

      if not (i % 16 - 7):
         print("- ", end='')

      if not (i % 16 - 15):
         print(" ")

   print("")

def sniffing(nic):
   if os.name == 'nt':
      address_familiy = socket.AF_INET
      protocol_type = socket.IPPROTO_IP
   else:
      address_familiy = socket.AF_PACKET
      protocol_type = socket.ntohs(ETH_P_ALL)

   with socket.socket(address_familiy, socket.SOCK_RAW, protocol_type) as sniffe_sock:
      sniffe_sock.bind((nic, 0))

      if os.name == 'nt':
         sniffe_sock.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)
         sniffe_sock.ioctl(socket.SIO_RCVALL,socket.RCVALL_ON)
      
      while(1) :                 ## 패킷을 계속 받아옴.
         data, _ = sniffe_sock.recvfrom(65535)

         print("[2] IP_PACKET-----------------------------\n")
         ethernet_header = make_ethernet_header(data[:ETH_SIZE])
         if ethernet_header == 1 :
            print("IP패킷이 아닙니다.")
            break
         else :                     ## Ethernet_header parsing후 Ethernet_type이 ip일경우
            print("Ethernet Header")
            for item in ethernet_header.items() :
               print('{0} : {1}' .format(item[0], item[1]))

            ip_headerLen = (int(data[14]) % 16 * 4)           ## ip 헤더 길이
            ip_header = make_IP_header(data[ETH_SIZE:ip_headerLen + 14])  
         
            print("\nIP HEADER")
            for item in ip_header.items() :
               print('{0} : {1}' .format(item[0], item[1]))

            print("\nRaw Data")
            dumpcode(data)

      if os.name == 'nt':
         sniffe_sock.ioctl(socket.SIO_RCVALL,socket.RCVALL_OFF)

if __name__ == '__main__':
   parser = argparse.ArgumentParser(description='This is a simpe packet sniffer')
   parser.add_argument('-i', type=str, required=True, metavar='NIC name', help='NIC name')
   args = parser.parse_args()

   sniffing(args.i)