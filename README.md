# Kube1s
- https://hub.docker.com/_/httpd

# BUILD & RUN
```bash
# BUILD
$ docker build -t my-apache2 .

# RUN
$ docker run -dit --name my-running-app -p 8949:80 my-apache2

# LOGIN CONTAINER
$ docker exec -it my-running-app bash
```
