FROM metacubex/mihomo:latest
LABEL maintainer="frzquantum <frzquantum@gmail.com>"
WORKDIR /opt/frp
ADD ./frp_onekey.sh /opt/frp/
ADD ./frpc.toml /opt/frp/
RUN chmod +x frp_onekey.sh
RUN bash frp_onekey.sh -a install -c frpc

ADD ./config.yaml /root/.config/mihomo
ENTRYPOINT ["bash"] 
