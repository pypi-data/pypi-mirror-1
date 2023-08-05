#!/bin/bash

FILE="<<zope_instance>>/log/firstrun.log"
PID=`cat <<zope_instance>>/var/firstrun.pid`

echo "Polling for zope:  ${FILE} , ${PID}"


while ! grep 'Zope Ready to handle requests' "${FILE}"
do

  if ! ps ${PID} > /dev/null
  then # zope has stopped
    cat ${FILE}
    echo "Zope failed to start :("
    exit 1
  fi
  
  sleep 1
done

echo "Zope started successfully :)"

exit 0