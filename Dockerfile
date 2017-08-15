FROM centos:7

# man pages for huckle
RUN bash
RUN yum install -y man

RUN cd /tmp
RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
RUN python2.7 get-pip.py

RUN pip install huckle

#ENTRYPOINT [ "huckle" ]
CMD [ "/bin/bash" ]
