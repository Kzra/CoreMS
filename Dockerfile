FROM python:latest
WORKDIR /home/enviroms/
#VOLUME  . /home/enviroms/

COPY  enviroms/ /home/enviroms/
COPY  requirements.txt LICENSE README.md setup.py /home/enviroms/
RUN pip install virtualenv
RUN virtualenv mypython
RUN python -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('win_only/__init__.py')]"
RUN . /home/enviroms/mypython/bin/activate
RUN pip install -r requirements.txt
RUN pip install wheel
RUN python setup.py sdist bdist_wheel
RUN python setup.py bdist_wheel
RUN pip install dist/*
#RUN deploy to PyPi 
#RUN build cli
#RUN deploy to dockerhub 

