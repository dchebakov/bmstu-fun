#!/bin/bash

NAME=BOLT_PROJECT
HOMEDIR=/home/chad/BOLT_PROJECT/
DJANGODIR=${HOMEDIR}/src/${NAME}
#SOCKFILE=/tmp/${NAME}.sock

NUM_WORGERS=3
DJANGO_WSGI_MODULE=${NAME}.wsgi
GUNICORN=${HOMEDIR}/env/bin/gunicorn

cd $HOMEDIR/src
source ${HOMEDIR}/env/bin/activate

#RUNDIR=$(dirname $SOCKFILE)
#test -d $RUNDIR || mkdir -p $RUNDIR

exec ${GUNICORN} ${DJANGO_WSGI_MODULE}:application \
    --workers $NUM_WORGERS \
    --bind=localhost:12345 \
    --log-file ${HOMEDIR}/logs/gunicorn.log
