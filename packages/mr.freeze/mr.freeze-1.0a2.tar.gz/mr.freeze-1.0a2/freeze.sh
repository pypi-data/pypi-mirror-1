#!/bin/bash

# This script finds a running Zope process by grepping the output of ps,
# then sends it a freeze signal.

if [ -n "$TM_FILEPATH" -a -n "$TM_LINE_NUMBER" ]; then
  path=$TM_FILEPATH
  line=$TM_LINE_NUMBER
else
  path=$1
  line=$2
fi

pid=$( ps -x | grep 'lib/python/Zope2/Startup/run.py' | tail +2 | tail -n 1 | awk '{print $1}' - )
if [ -n "$pid" ]; then
  lock=$( lsof -F -p $pid | grep '^n.*/instance\.lock$' )
  freeze=$( echo $lock | cut -c2- | sed 's/lock$/freeze/' )
  path=$( readlink -f "$path" )
  echo -e "freeze $path $line\npony" > "$freeze"
  echo "set up freeze file at $freeze:"
  cat "$freeze"
  kill -SIGUSR1 $pid
  sleep 1
else
  echo 'No running zope found.'
fi
