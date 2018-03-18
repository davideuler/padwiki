#!/bin/sh
rm db
ln db.lucene db -s
cd mywiki
python manage.py runserver 
