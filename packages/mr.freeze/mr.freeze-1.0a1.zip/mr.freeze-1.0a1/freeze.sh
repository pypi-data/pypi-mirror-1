#!/bin/bash

if [ -n "$TM_FILEPATH" -a -n "$TM_LINE_NUMBER" ]; then
  path=$TM_FILEPATH
  line=$TM_LINE_NUMBER
else
  path=$1
  line=$2
fi

url=$( osascript -e '
  tell application "Safari"
    activate
    set myURL to URL of document 1 as text
    do shell script "echo \"" & myURL & "\""
  end tell' )

if [[ "$url" =~ ^http://[^:]*:([0-9]*)/ ]]; then
  port=${BASH_REMATCH[1]}
  pid=$( lsof -nF -itcp:$port | grep ^p | tr -d p | sort -nr | head -1 )
  lock=$( lsof -F -p $pid | grep '^n.*/instance\.lock$' )
  freeze=$( echo $lock | cut -c2- | sed 's/lock$/freeze/' )
  path=$( readlink -f "$path" )
  echo -e "freeze $path $line\npony" > "$freeze"
  echo "set up freeze file at $freeze:"
  cat "$freeze"
  kill -SIGUSR1 $pid
  sleep 1
  osascript -e '
    tell application "System Events"
      tell process "Safari"
        keystroke "r" using {command down}
      end tell
    end tell'
fi
