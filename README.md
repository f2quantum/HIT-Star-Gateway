# 誘導已亮，前方淨空
Harbin Institute of Technology 远程注册服务

## 构建容器
把`frpc.toml` 装入`/config/frpc.toml` 位置
``` bash
make build
```
## 启动
```
# nat 模式
docker run -itd --name hit-star-gateway frzquantum/hit-star-gateway:1.0
# host net 模式
docker run -itd --name hit-star-gateway --net=host frzquantum/hit-star-gateway:1.0
```
## 查看日志

``` shell
docker exec -it hit-star-gateway bash
tail -f /var/log/mihomo.out.log
tail -f /var/log/frpc.out.log
``` 