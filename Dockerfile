############################################################
# Dockerfile to start the XtremPerfProb
# Based on Python 2.7
############################################################
FROM python:2.7

# Update the repository sources list
RUN apt-get update

################## BEGIN INSTALLATION ######################
RUN pip install --upgrade pip
RUN pip install pyVmomi
RUN pip install numpy
RUN pip install matplotlib

# Install from Repo
WORKDIR /home/
RUN git clone https://github.com/nachiketkarmarkar/XtremPerfProbe
RUN git clone https://github.com/nachiketkarmarkar/PyXtrem
RUN cp -a /home/PyXtrem/. /home/XtremPerfProbe/
WORKDIR /home/XtremPerfProbe/

# Set default container command
ENTRYPOINT ["python"]