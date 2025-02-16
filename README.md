# 誘導已亮，前方淨空
Harbin Institute of Technology 远程注册服务

## 搭建frps
你可以参考：`example/frps.ini` 下面的配置文件

## 构建容器
把你的`frpc.toml` 修改后装入`/config/frpc.toml` 位置
执行下面的命令

``` bash
make build
```

或者是

``` bash
docker build -t {YOUR_USERNAME}/hit-star-gateway:{YOUR_VERSION} . 
```
## 启动
两种方法应该都可以
```
# nat 模式
docker run -itd --name hit-star-gateway frzquantum/hit-star-gateway:1.1
# host net 模式
docker run -itd --name hit-star-gateway --net=host frzquantum/hit-star-gateway:1.1
```
## 查看日志

``` shell
docker exec -it hit-star-gateway bash
tail -f /var/log/mihomo.out.log
tail -f /var/log/frpc.out.log
``` 