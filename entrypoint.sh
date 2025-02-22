#!/bin/bash 
echo "root:HitStar-Gateway-Service" | chpasswd
sed -i "s/name = \"hit-star-gateway\"/name = \"hit-star-gateway-$(date +%s)\"/" /opt/hit-star-gateway/frpc.toml
/usr/bin/supervisord -c /etc/supervisord.conf
bash 
