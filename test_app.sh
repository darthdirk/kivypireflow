#! /bin/bash

APP="Kiflow.py"
START="python3"

export DEBUG_KIVY=1

while true; do

	echo "STARTING"
	${START} ${APP} | grep -iv gtk
	if [ "$?" -ne "0" ] ; then
		echo "STOPPING 1"
		sleep 1
	fi

done