FROM ubuntu:14.04

RUN apt-get -y update && apt-get install -y git

RUN apt-get install -y python python-pip python-dev \

  python-setuptools \

  python-numpy \

  python-lxml \

  python-qt4

RUN apt-get install -y wget

RUN git clone https://github.com/adrlar/CanSNPer.git

RUN cd CanSNPer && \
  
  python setup.py install

RUN wget http://darlinglab.org/mauve/snapshots/2015/2015-02-13/linux-x64/mauve_linux_snapshot_2015-02-13.tar.gz

RUN tar -xvf mauve_linux_snapshot_2015-02-13.tar.gz

RUN cp mauve_snapshot_2015-02-13/linux-x64/progressiveMauve /usr/local/bin/

RUN apt-get install -y xvfb

RUN chmod a+x /CanSNPer/docker_script.sh
