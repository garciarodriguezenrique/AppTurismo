!#/bin/sh


echo "Restarting MySQL..."
/etc/init.d/mysql restart

echo "Creating database..."
mysql -u root < script.sql

echo "Configuring Django user..."
cat mycnf >> /etc/mysql/my.cnf

echo "Launching Web Service on 0.0.0.0:8000..."
python /code/tfg_webservice/manage.py migrate
python /code/tfg_webservice/manage.py runserver 0.0.0.0:8000 &

echo "Launching TourismApp on 0.0.0.0:8005..."
python /code/TourismApp/manage.py runserver 0.0.0.0:8005
