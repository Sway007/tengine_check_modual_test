
<link href="style.css" rel="stylesheet" type="text/css"><link >

# HTTP协议健康检查

## 被动(passive)健康检查

#### overview

  > 当连接失败时Nginx检测到服务器不可达，并试图重建立失败的连接，当重建次数超过设定的参数(max_fails)时，该服务器被标志为不可达(unavailable),并且暂时(fail_timeout)停止向它发送请求直到被宠幸标记为可达(available).

#### 参数

- `fail_timeout`

    如果在设定的时间内失败次数达到`max_fails`，则将服务器标记为unavailable，并在同等的时间内不想该服务器发送请求。

- `max_fails`

> 如果服务器组只有一个机器，则`fail_timeout`,`max_fails`被忽略，服务器永远不会被标记为unavailable.


### 慢启动

- `slow_start`

    在`upstream` `server` 里指定，允许恢复的服务器在给定的时间内逐渐地将权值(weight)恢复为最初给定的值。

## 主动健康检查

#### overview

> 定期发送特殊的health-check请求给每个服务器，验证相应的response.

- 启动主动健康检查

    在`location`块里讲请求代理给upstream group, 并包含`health_check`指令

    ```
    server {
        location / {
            proxy_pass http://backend;
            health_check;
        }
    }
    ```

- `zone`

    需要在`upstream`块里包含`zone`指令，使得多个工作进程共享相应的配置参数，如`passes`, `fails`, `interval`等。   
    如果不包含则多个工作进程保留一份属于自己的配置参数信息。

- `interval`

    健康检查请求的间隔时间

- `fails`

    指定服务器标记为unavailable的条件: 请求连续失败指定的次数

- `passes`

    指定服务器标记为available的条件: 连续成功的次数

- `uri`

    为health check请求地址添加指定的后缀
    ```
    upstream backend {
        zone backend 64k;
        server backend1.example.com;
        server backend2.example.com;
        server backend3.example.com;
        server backend4.example.com;
    }
    location / {
        proxy_pass http://backend;
        health_check uri=/some/path;
    }
    ```
    上述配置的health_check请求uri为*http://backend1.example.com/some/path.*

### 自定义条件

- `match`

    自定义条件定义在`match`块，在`health_check`指令里用参数`match`引用。
    ```
    http {
        ...
        match server_ok {
            status 200-399;
            body !~ "maintenance mode";
        }
        server {
            ...
            location / {
                proxy_pass http://backend;
                health_check match=server_ok;
            }
        }
    }
    ```
    http请求的自定义条件可以检查状态码(status code)，response (header and body)
    > match指令里正则表达式以`~`开头， 以`!`表示否定

# TCP协议健康检查

## 被动健康检查

配置参数及其意义和HTTP协议被动健康检查一样

## 主动健康检查

- `health_check_timeout` ?? 

    `health_check_timeout overrides the proxy_timeout value for health checks, as for health checks this timeout needs to be significantly shorter.`  
    proxy_timeout: ets the timeout between two successive read or write operations on client or proxied server connections. If no data is transmitted within this time, the connection is closed.

    Q: _主动健康检查请求的间隔时间不是由`interval`参数指定了吗？_

- `port`

    健康请求发送的接口默认是upstream server里指定的端口号，也可以为健康请求单独指定一个端口号，用`health_check`指令`prot`参数指定

- TCP协议`match`配置块

    - `send` 

        发送给服务器的字符串或16进制码

    - `expecet`

        期望服务器返回的字符串或者匹配的正则表达式

    - 如果没有指定`send`, `expect`参数，则只检测与服务器之间的连接

    ```
    stream {
        ...
        upstream   stream_backend {
            zone   upstream_backend 64k;
            server backend1.example.com:12345;
        }
        match http {
            send      "GET / HTTP/1.0\r\nHost: localhost\r\n\r\n";
            expect ~* "200 OK";
        }
        server {
        listen       12345;
        health_check match=http;
        proxy_pass   stream_backend;
        }
    }
    ```
    上述配置中，为了健康检查通过，必须想服务器发送一个HTTP请求，从服务器期待的返回必须包含 `220 OK`


Q: <p class='question'>因为HTTP协议是给予TCP协议传输的，那么如果配置文件里同事配置了http模块和stream模块，且Stream模块里定义了监听80端口的server，那么一个正常的http请求nginx会交给http还是stream模块里定义的server处理呢？</p>

参考地址:  
- [Nginx_admin_guide](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/)
- [Nginx_admin_guide_HTTP_Health_checks](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-health-check/)
- [Nginx_admin_guide_TCP_Health_checks](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-health-check/)