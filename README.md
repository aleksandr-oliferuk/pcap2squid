# pcap-dump parser to squid-proxy log format

## Description

Recieve raw network trafic dump in [pcap-format](https://en.wikipedia.org/wiki/Pcap) and parse it to [squid-proxy](http://www.squid-cache.org/) log. Then generate report for [lightsquid](http://lightsquid.sourceforge.net/) and shows it in Web UI.

## Usage

Clone this project, complete [.env](.env) with your values, then run it with `docker-compose up -d`

After that you shoul setup your [cron](https://en.wikipedia.org/wiki/Cron) on host machine with something like this:

```
*/5 * * * * docker exec lightsquid_app_1 ./lightparser.pl today 2>> $PROJ_PATH/errors.log
0 4 * * * rm -f $PROJ_PATH/log/access.log
```

Report will appear at `http://$LIGHTSQUID_ADDR:$LIGHTSQUID_LISTEN_PORT`

## Enviroment example

```
# Path, where you download this project
PROJ_PATH="/srv/pcap2squid"

# Lightsquid vars
LIGHTSQUID_ADDR="192.168.1.1"
LIGHTSQUID_LISTEN_PORT=80
```

## Some advices

The best way to use ramdisk for all processed files. E.g. of fstab:

```
tmpfs   $PROJ_PATH/dump   tmpfs   rw,size=500M    0       0
tmpfs   $PROJ_PATH/log   tmpfs   rw,size=5G        0       0
```

To change language of lightsquid report just change `$lang` parameter in [lightsquid.cfg](./lightsquid/lightsquid-1.8/lightsquid.cfg) and rebuild lightsquid image.

If you are using [phpIPAM](https://phpipam.net/), you could using my [script](get-names.py) to complete lightsquid report with real names of ip-addrs users (realname.cfg).