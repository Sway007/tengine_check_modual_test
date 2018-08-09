# tengine_check_modual_test

## Experiment steps:

1. install docker
2. compile health check modual into nginx
3. overwrite the default nginx.conf with nginx.conf-cp
4. reload nginx
5. run the following commands
    ```shell
    docker run -p 4001:80 flask_app -n 1  # for node 1
    docker run -p 4001:80 flask_app -n 2  # for node 2
    ```
6. visit http://localhost/status
