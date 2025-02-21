FROM metacubex/mihomo:latest
LABEL maintainer="frzquantum <frzquantum@gmail.com>"
WORKDIR /opt/hit-star-gateway

ADD ./config/config.yaml /root/.config/mihomo
ADD ./entrypoint.sh /opt/hit-star-gateway
ADD ./exec/frpc /opt/hit-star-gateway/
ADD ./config/frpc.toml /opt/hit-star-gateway/
ADD ./service/client /opt/hit-star-gateway/client

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk add --no-cache bash supervisor openssh-server python3 py3-pip

RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple \
    && pip3 install -r /opt/hit-star-gateway/client/requirements.txt --break-system-packages
RUN chmod +x /opt/hit-star-gateway/frpc \
    && mkdir -p /var/log/supervisor \
    && mkdir -p /etc/supervisor/conf.d 

RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && ssh-keygen -A


ADD ./config/supervisor /etc/supervisor.d/
#ENTRYPOINT ["sh"]
ENTRYPOINT [ "bash","entrypoint.sh" ]
