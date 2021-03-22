FROM amazonlinux:2.0.20191217.0


COPY pyswitch /usr/bin/
RUN chmod +x /usr/bin/pyswitch

RUN mkdir -p /opt
COPY aws_setup /opt/
RUN chmod +x /opt/aws_setup

RUN yum update -y &&\
    amazon-linux-extras install -y python3

# Install node
RUN curl --silent --location https://rpm.nodesource.com/setup_14.x | bash -
RUN yum install nodejs -y && npm install -g serverless

RUN npm install -g serverless

RUN rm /usr/bin/python &&\
    ln -s /usr/bin/python3 /usr/bin/python && \
    pyswitch 3 &&\
    pip install --user virtualenv

VOLUME /aws/host:ro
VOLUME /code

ENV AWS_PROFILE=default
ENV AWS_DEFAULT_REGION=us-east-1

CMD /opt/aws_setup && tail -f /dev/null
