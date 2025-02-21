#!/bin/bash 
echo "root:HitStar-Gateway-Service" | chpasswd
/usr/bin/supervisord -c /etc/supervisord.conf
bash 
