FROM python:3

# apt 使用镜像
RUN curl -s http://mirrors.163.com/.help/sources.list.jessie > /etc/apt/sources.list || true

# 安装开发所需要的一些工具，同时方便在服务器上进行调试
RUN apt-get update;\
    apt-get install -y vim;\
    true

COPY aibot_sanic/requirements.txt /opt/app/
WORKDIR /opt/app

# 使用镜像下载
RUN pip install -r requirements.txt -i https://pypi.doubanio.com/simple --trusted-host pypi.doubanio.com || \
    pip install -r requirements.txt
