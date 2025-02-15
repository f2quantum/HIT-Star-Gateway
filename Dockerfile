FROM metacubex/mihomo:latest
LABEL maintainer="frzquantum <frzquantum@gmail.com>"
WORKDIR /opt/hit-star-gateway
ADD ./config/config.yaml /root/.config/mihomo
ADD ./entrypoint.sh /opt/hit-star-gateway
ADD ./exec/frpc /opt/hit-star-gateway/
ADD ./config/frpc.toml /opt/hit-star-gateway/
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g'\
    /etc/apk/repositories &&\
    chmod +x /opt/hit-star-gateway/frpc &&\
    apk add --no-cache bash supervisor  &&\
    mkdir -p /var/log/supervisor &&\
    mkdir -p /etc/supervisor/conf.d

ADD ./config/supervisor/frpc.ini /etc/supervisor.d/
ADD ./config/supervisor/mihomo.ini /etc/supervisor.d/
#ENTRYPOINT ["sh"]
ENTRYPOINT [ "bash","entrypoint.sh" ]
