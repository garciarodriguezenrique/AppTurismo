#Dockerfile
FROM python:3.5

RUN apt-get update
RUN apt-get install -y mysql-server

RUN mkdir /code

RUN git clone https://github.com/garciarodriguezenrique/AppTurismo
RUN mv AppTurismo/django-rest/tfg_webservice /code
RUN mv AppTurismo/django-projects/TourismApp /code

WORKDIR /code/tfg_webservice

COPY requirements.txt /code/tfg_webservice/
COPY script.sql /code/tfg_webservice/
COPY mycnf /code/tfg_webservice/
COPY conf-script.sh /code/tfg_webservice/
RUN chmod +x /code/tfg_webservice/conf-script.sh
RUN pip install -U pip
RUN pip install pandas
RUN pip install django_user_agents
RUN pip install -Ur requirements.txt

EXPOSE 8000
EXPOSE 8005

CMD /code/tfg_webservice/conf-script.sh




