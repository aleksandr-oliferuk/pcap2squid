#!/usr/local/bin/python

# squid log format:
# time (timestamp) elapsed (dummy) remotehost (src_ip) code/status (dummy) bytes (length) method (dummy) URL (host) rfc931 (-) peerstatus/peerhost (dst_ip) type (dummy)

import dpkt
from socket import inet_ntop, AF_INET, AF_INET6
from re import findall


def inet_to_str(inet):
    try:
        return inet_ntop(AF_INET, inet)
    except ValueError:
        return inet_ntop(AF_INET6, inet)


f = open('/var/parser/dump/dump.pcap')
pcap = dpkt.pcap.Reader(f)

for timestamp, buf in pcap:
    try:
        pac_len = len(buf)
        eth = dpkt.ethernet.Ethernet(buf)
        ip = eth.data
        ip_len = ip.len

        tcp = ip.data
        tcp_dat = tcp.data
        tcp_len = len(tcp_dat)

        src_ip = inet_to_str(ip.src)
        src_port = tcp.sport

        dst_ip = inet_to_str(ip.dst)
        dst_port = tcp.dport

        if tcp_len > 0:

            if dst_port == 80:
                http = dpkt.http.Request(tcp_dat)
                host_http = str(http.headers.get('host'))

                if host_http == 'None':
                    host_http = dst_ip

                print '{} 0 {} TAG_NONE/400 {} GET http://{}{} - ORIGINAL_DST/{} text/html'.format(timestamp, src_ip, pac_len, host_http, http.uri, dst_ip)

            elif dst_port == 443:
                stream = tcp_dat
                records, bytes_used = dpkt.ssl.tls_multi_factory(stream)

                if len(records) > 0:
                    for record in records:
                        if record.type == 22:
                            handshake = dpkt.ssl.TLSHandshake(record.data)

                            if isinstance(handshake.data, dpkt.ssl.TLSClientHello):
                                ch = handshake.data
                                myregex = r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}'
                                host_https = str(findall(myregex, ch.data)).strip("[").strip("]").strip("'")

                                if host_https == '':
                                    host_https = dst_ip

                                print '{} 0 {} TAG_NONE/400 {} GET https://{} - ORIGINAL_DST/{} text/html'.format(timestamp, src_ip, pac_len, host_https, dst_ip)

        else:
            continue

    except(dpkt.NeedData, dpkt.ssl.SSL3Exception, dpkt.dpkt.UnpackError, AttributeError, ValueError):
        continue

f.close()
