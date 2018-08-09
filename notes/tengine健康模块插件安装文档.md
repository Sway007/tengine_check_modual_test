# 将tengine健康检查模块(check modual)编译安装到nginx

- nginx版本号1.12.1
- 下载tengine[健康检查模块插件](https://github.com/yaoweibin/nginx_upstream_check_module)

    ```shell
    wget https://codeload.github.com/yaoweibin/nginx_upstream_check_module/zip/master
    ```

- 将健康检查模块编译进nginx源码包

    ```
    cd nginx-1.12.1   #进入nginx源码包
    patch -p1 < ${path/to/check_modual}/check_1.5.12+.patch   # 为nginx源码打补丁
    ./config --user=nginx --group=nginx --prefix=/usr/local/nginx-1.6.0 --with-http_ssl_module --with-openssl=/usr/local/src/openssl-0.9.8q --with-pcre=/usr/local/src/pcre-8.32 --add-module=/usr/local/src/nginx_concat_module/ --add-module=${path/to/checck_modual}  # 设置编译参数
    make   # 编译
    make install  # 安装
    /usr/local/nginx/sbin/nginx -v  # 测试安装成功
    ```

# 测试安装成功的健康检车模块相关指令及其参数

- 利用docker在本地启动2台运行http server的vm

    ```
    # 在4000端口运行编号为1的http server
    docker run -p 4000:80 yansw007/vms:flask_node -n 1
    ```
    ```
    # 在4001端口运行编号为2的http server
    docker run -p 4001:80 yansw007/vms:flask_node -n 2
    ```

- nginx配置文件

    ```nginx.conf
    worker_processes  1;


    events {
        worker_connections  1024;
    }


    http {
        include       mime.types;
        default_type  application/octet-stream;

        sendfile        on;

        keepalive_timeout  65;


        upstream dockervms {
            server localhost:4000;   # node 1
            server localhost:4001;   # node 2

            # 配置健康检查模块相关参数
            check interval=3000 rise=2 fall=2 timeout=1000 type=http;
            check_http_send "HEAD / HTTP/1.0\r\n\r\n";
            check_http_expect_alive http_2xx http_3xx;
        }

        server {
            listen       80;
            server_name  localhost;


            location / {
                proxy_pass http://dockervms;
            }

            # redirect server error pages to the static page /50x.html
            #
            error_page   500 502 503 504  /50x.html;
            location = /50x.html {
                root   html;
            }

        }

    }
    ```

- 查看并测试nginx运行结果

    1. 在两台vm里都有每个3秒收到来自nginx发送的HEAD请求，说明nginx `interval`参数运行正常
    
    <img src='imgs/interval.png'>