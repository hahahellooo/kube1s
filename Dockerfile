FROM httpd:2.4
COPY ./my-httpd.conf /usr/local/apache2/conf/httpd.conf
ARG REPO_URL=https://github.com/hahahellooo/hahahellooo.github.io.git

RUN ["apt-get", "update"]
RUN ["apt-get", "install","-y", "vim"]
RUN ["apt-get", "install", "-y", "git"]
RUN git clone ${REPO_URL} /usr/local/apache2/blog
