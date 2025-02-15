FROM metacubex/mihomo:latest
LABEL maintainer="frzquantum <frzquantum@gmail.com>"
WORKDIR /opt/frp
ADD ./exec/frpc /opt/frp/
ADD ./frpc.toml /opt/frp/
RUN chmod +x /opt/frp/frpc

ADD ./config.yaml /root/.config/mihomo
# ENTRYPOINT ["/opt/frp/frpc","-c","/opt/frp/frpc.toml"] 

ENTRYPOINT [ "sh" ]
