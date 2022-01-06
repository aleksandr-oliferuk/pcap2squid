import socket
import struct
from mysql.connector import connect


def long2ip(ipaddr):
    try:
        ipaddr = socket.inet_ntoa(struct.pack("!I", int(ipaddr)))
    except struct.error:
        return False

    return ipaddr
    

ipamdb = connect(host="IPAM_URL",user="IPAM_USERNAME",password="IPAM_PWD")
cursor=ipamdb.cursor(buffered=True)
query='SELECT ip_addr,owner FROM phpipam.ipaddresses WHERE owner IS NOT NULL AND owner != "?" AND owner != "" AND owner != "no_body";'
cursor.execute(query)
data=cursor.fetchall()

for item in data:
    decimal_addr = item[0]
    owner = item[1]
    ipaddr = long2ip(decimal_addr)

    if ipaddr == False:
        pass
    else:
        print(ipaddr, owner)

exit(0)
