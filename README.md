# pcap-dump parser to squid-proxy log format

## Description

Recieve raw network trafic dump in [pcap-format](https://en.wikipedia.org/wiki/Pcap) and parse it to [squid-proxy](http://www.squid-cache.org/) log. Then generate report for [lightsquid](http://lightsquid.sourceforge.net/) and shows it in Web UI.

This implementation get traffic from [mikrotik sniffer](https://wiki.mikrotik.com/wiki/Manual:Tools/Packet_Sniffer) on udp port 37008 and parse it with [trafr](http://www.mikrotik.com/download/trafr.tgz) program. You could rebuild [parser](./parser/Dockerfile) image without it and recieve trafic just with [tcpdump](https://www.tcpdump.org/manpages/tcpdump.1.html).

With this tool you will get statistics, which sites and when watch users of your LAN. But it doesn't give you actual trafic amount.

## Usage

Clone this project, complete [.env](.env) with your values, then run it with `docker-compose up -d`

After that you should setup your [cron](https://en.wikipedia.org/wiki/Cron) on host machine with something like this:

```
*/5 * * * * docker exec pcap2squid_lightsquid_1 ./lightparser.pl today 2>> $PROJ_PATH/errors.log
0 4 * * * rm -f $PROJ_PATH/log/access.log
```

Report will appear at `http://$LIGHTSQUID_ADDR:$LIGHTSQUID_LISTEN_PORT`

## Environment example

```
# Path, where you download this project
PROJ_PATH="/srv/pcap2squid"

# Lightsquid vars
LIGHTSQUID_ADDR="192.168.1.1"
LIGHTSQUID_LISTEN_PORT=80
```

## Some advices

The best way to use [ramdisk](https://en.wikipedia.org/wiki/Tmpfs) for all processed files. E.g. of fstab:

```
tmpfs   $PROJ_PATH/dump   tmpfs   rw,size=500M    0       0
tmpfs   $PROJ_PATH/log   tmpfs   rw,size=5G        0       0
```

To change language of lightsquid report just change `$lang` parameter in [lightsquid.cfg](./lightsquid/lightsquid-1.8/lightsquid.cfg) and rebuild [lightsquid](./lightsquid/Dockerfile) image.

If you are using [phpIPAM](https://phpipam.net/), you could use my [script](get-names.py) to complete lightsquid report with real names of ip-addrs owners (realname.cfg).