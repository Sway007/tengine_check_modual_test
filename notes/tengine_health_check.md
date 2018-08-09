
# 完整例子

```c
http {
    upstream cluster1 {
        # simple round-robin
        server 192.168.0.1:80;
        server 192.168.0.2:80;

        check interval=3000 rise=2 fall=5 timeout=1000 type=http;
        check_http_send "HEAD / HTTP/1.0\r\n\r\n";
        check_http_expect_alive http_2xx http_3xx;
    }

    upstream cluster2 {
        # simple round-robin
        server 192.168.0.3:80;
        server 192.168.0.4:80;

        check interval=3000 rise=2 fall=5 timeout=1000 type=http;
        check_keepalive_requests 100;
        check_http_send "HEAD / HTTP/1.1\r\nConnection: keep-alive\r\n\r\n";
        check_http_expect_alive http_2xx http_3xx;
    }

    server {
        listen 80;

        location /1 {
            proxy_pass http://cluster1;
        }

        location /2 {
            proxy_pass http://cluster2;
        }

        location /status {
            check_status;

            access_log   off;
            allow SOME.IP.ADD.RESS;
            deny all;
        }
    }
}
```

## Tengine路径

- 安装路径 `/usr/local/nginx/`
- 配置文件路径 `/usr/local/nginx/conf/nginx.conf`

## 安全检查模块相关指令

> Syntax: `check interval=milliseconds [fall=count] [rise=count] [timeout=milliseconds] [default_down=true|false] [type=tcp|http|ssl_hello|mysql|ajp] [port=check_port]`
> 默认参数: `interval=30000 fall=5 rise=2 timeout=1000 default_down=true type=tcp`
> Contex: `upstream`

> 与Nginx安全检查模块不同的点:
> 
> 1. 启动命令是`check`而非`health_check`
> 2. Contex是`upstream`而非`server`

- `interval`: 向后端发送的健康检查包的间隔。
- `fall`: 如果连续失败次数达到fall_count，服务器就被认为是down。
- `rise`: 如果连续成功次数达到rise_count，服务器就被认为是up。
- `timeout`: 后端健康请求的超时时间。
- `default_down`: 设定初始时服务器的状态，如果是true，就说明默认是down的，如果是false，就是up的。默认值是true，也就是一开始服务器认为是不可用，要等健康检查包达到一定成功次数以后才会被认为是健康的。
- `type`: 健康检查包的类型，现在支持以下多种类型
    - `tcp`: 简单的tcp连接，如果连接成功，就说明后端正常。
    - `ssl_hello`: 发送一个初始的SSL hello包并接受服务器的SSL hello包。
    - `http`: 发送HTTP请求，通过后端的回复包的状态来判断后端是否存活。
    - `mysql`: 向mysql服务器连接，通过接收服务器的greeting包来判断后端是否存活。
    - `ajp`: 向后端发送AJP协议的Cping包，通过接收Cpong包来判断后端是否存活。
- `port`: 指定后端服务器的检查端口。你可以指定不同于真实服务的后端服务器的端口，比如后端提供的是443端口的应用，你可以去检查80端口的状态来判断后端健康状况。默认是0，表示跟后端server提供真实服务的端口一样。该选项出现于Tengine-1.4.0。

> Syntax: `check_keepalive_requests request_num`
> 默认参数: 1  
> Contex: `upstream`

该指令可以配置一个连接发送的请求数，其默认值为1，表示Tengine完成1次请求后即关闭连接。

> Syntax: `check_http_send http_packet`  
> 默认参数: "GET / HTTP/1.0\r\n\r\n"  
> Contex: `upstream`

配置http健康检查包发送的请求内容。为了减少传输数据量，最好采用"HEAD"方法

> Syntax: `check_http_expect_alive [ http_2xx | http_3xx | http_4xx | http_5xx ]`  
> 默认参数: http_2xx | http_3xx
> Contex: `upstream`

该指令指定HTTP回复的成功状态，默认认为2XX和3XX的状态是健康的。

> Syntax: check_shm_size size
> 默认参数: 1M
> Contex: `http`

所有的后端服务器健康检查状态都存于共享内存中，该指令可以设置共享内存的大小。如果服务器数量超过1千台以上并在配置的时候出现了错误，就可能需要扩大该内存的大小。  
相当于Nginx的`Zone`指令