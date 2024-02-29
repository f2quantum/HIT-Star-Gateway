# HIT-Star-Gateway
Harbin Institute of Technology 远程注册服务


## 启动

``` bash

docker run --name mihomo -d \
    -p 7890:7890 \
    -p 7891:7891 \
    -p 7892:7892 \
    -p 9090:9090 \
    -v /path/to/config:/root/.config/mihomo \
    izumiko/mihomo

```