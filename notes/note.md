# Nginx Beginner Guide

### 1. nginx has *one master process* and several worker processes

- The main purpose of the master process is to read and evaluate configuration, and maintain worker processes.
    - Worker processes do actual processing of requests.

### 2. The way nginx and its modules work is determined in the configuration file
- By default, `nginx.conf`
    - `/usr/local/nginx/conf`; `/etc/nginx`; `/usr/local/etc/nginx`

    location in my ubuntu machine: `/etc/nginx/nginx.conf`

### 3. start, stop and reload commands

> nginx -s _signal_

 - the _signal_ could be:  
    - stop
    - quit
    - reload
    - reopen

 - signal may also be sent to process with unix command `kill`, the master pid of nginx is written to `/usr/local/nginx/logs` or `/var/run`. in my machine, the location is `/var/run/nginx.pid`. so the quit siginal can also be sent by:
    > kill -s QUIT _pid_
    - the nginx pid can also be found by
        ```
        ps -ax | grep nginx
        ```

### 4. Configuration File’s Structure `/etc/nginx/nginx.conf`

- *simple directive* and *block directive*
    - A simple directive consists of the name and parameters separated by spaces and ends with a semicolon (;).
    - A block directive has the same structure as a simple directive, but instead of the semicolon it ends with a set of additional instructions surrounded by braces ({ and })

- *context*
    - If a block directive can have other directives inside braces, it is called a context 

- _location_ directiv

    ```markdown
    location *prefix* {
        root  */path/on/local/machine*
    }
    ```

- Setting Up a Simple Proxy Server

    add following directive `proxy_pass` in the location context:
    ```
    location / {
        proxy_pass http://localhost:8080;
    }
    ```

    - prefix can be regular expression: preceded with `~`
        
        - `~ regular expression`
        - first check specified prefix, then checks regular expressions.


# NGINX

### 1. master process

- read and evaluate configuration files
- maintain worker processes.

### 2. contex inheritance and override

### 3. Proxying HTTP Traffic to a Group of Servers

- define server group using `upstream`
- pass requests to a server group using `proxy_pass`
- `backup` server does not receive requests unless all the other servers are unavailable.

    ```
    http {
        upstream backend {
            server backend1.example.com;
            server backend2.example.com;
            server 192.0.0.1 backup;
        }
    
        server {
            location / {
                proxy_pass http://backend;
            }
        }
    }
    ```

### 4. Available Load-Balancing Methods in Nginx

- Round Robin (default)
- Least Connections 
- IP Hash 
- Generic Hash 
- Least Time (Nginx Plus only)

    ```markdown
    upstream backend {
        *load_balance_method*;
        server backend1.example.com;
        server backend2.example.com;
    }
    ```

### 5. Health Checks

1. passive health checks

    - `max_fails`
    - `fail_timeout`

    ```
    upstream backend {
        server backend1.example.com;
        server backend2.example.com max_fails=3 fail_timeout=30s;
        server backend3.example.com max_fails=2;
    }
    ```

2. Active Health Checks

    > Periodically sending special requests to each server and checking for a response that satisfies certain conditions can monitor the availability of servers.


    - include `health_check` directive in the location context that passes requests to an upstream group.
    - upstream group must include the `zone` directive to define a **_shared-memory zone where information about health status is stored_**

    ```
    http {
        upstream backend {
            zone backend 64k;
            server backend1.example.com;
            server backend2.example.com;
            server backend3.example.com;
            server backend4.example.com;
        }
        server {
            location / {
                proxy_pass http://backend;
                health_check;
            }
        }
    }
    ```

    - default `health_check`

        - every 5 seconds NGINX Plus sends a request for / to each server in the backend group
        - If any communication error or timeout occurs the health check fails for that server
        - Any server that fails a health check is considered _unhealthy_, and NGINX Plus stops sending client requests to it until it once again passes a health check.

    - `health_check` 参数
        - `interval` 健康检查时间间隔
        - `fails` 健康状态在`interval`内失败上限
        - `passes` 重回健康状态在`interval`内必须成功的次数
        - `uri` 发给server group请求地址前缀
        - `match` 自定义response必须满足的状态，可以指定status， header, body等字段


            ```
            http {
                # ...
                match server_ok {
                    status 200-399;
                    body !~ "maintenance mode";
                }
                
                server {
                    # ...
                    location / {
                        proxy_pass http://backend;
                        health_check match=server_ok interval=5 fails=3 passes=2 uri=/some/path;
                    }
                }
            }
            ```
            - match block 可以使用正则表达式制定满足条件
                - regex以 `~` 开头
                - 否定以 `！` 开头

### 6. 多工作进程共享数据区 `zone`

1. `zone`字段在`upstream`块指定， 如果没有指定`zone`区，则每个工作进程保留和维护各自的server group配置信息， 比如`fails`, `passes`, `max_fails`, `fail_timeout`等计数器

### 7. 利用DNS配置HTTP负载均衡

1. `resolver`
    1. dns 服务器地址
    2. `valid`: 指定重解析IP地址的时间间隔，默认由IP协议的TTL字段指定
    3. `ipv6`: 是否将域名解析成ipv6地址

2. `resolve`

    在upstream块内需要定期解析域名的服务器`server`指定后指定

```
http {
    resolver 10.0.0.1 valid=300s ipv6=off;
    resolver_timeout 10s;
    server {
        location / {
            proxy_pass http://backend;
        }
    }
    upstream backend {
        zone backend 32k;
        least_conn;
        # ...
        server backend1.example.com resolve;
        server backend2.example.com resolve;
    }
}
```

## TCP和UDP的负载均衡

1. 由`stream`指定块指定
2. `server`默认TCP

    ```markdown
    stream {
        server {
            listen *port* [udp];
        }
    }
    ```

3. `proxy_bind`指令可以指定路由服务器转发请求的特定接口

    ```
    stream {
        # ...
        server {
            listen     127.0.0.1:12345;
            proxy_pass backend.example.com:12345;
            proxy_bind 127.0.0.1:12345;
        }
    }
    ```

4. `health_check_timeout`

    覆盖`proxy_timeout`，指定两次连续成功的读写操作超时时间，如果超时，则链接终止。

5. TCP Health Check `match`块

    1. 如果`send`和`expect`都没有指定，则只检查和服务器的连接
    2. 如果`send`和`expect`都指定，则表明通过send参数发送给服务器得到的Response必须匹配expect的正则表达式

    ```
    stream {
        upstream stream_backend {
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
    上述例子表明：健康检查要通过，则 HTTP 请求一定要发送到服务器，并且从服务器返回的结果包含 200 OK 来指示这是一个成功的 HTTP 响应。

