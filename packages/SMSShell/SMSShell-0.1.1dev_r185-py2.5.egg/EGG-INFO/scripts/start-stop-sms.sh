#!/bin/bash
#start-stop-sms.sh

KANNEL=/etc/init.d/kannel
MGETTY=/etc/init.d/mgetty-fax

main() {
case "$1" in
    start)
      /etc/init.d/mgetty-fax start
      /etc/init.d/kannel start
      ;;
    stop)
      /etc/init.d/kannel stop
      /etc/init.d/mgetty-fax stop
      ;;
    restart)
      $0 stop
      sleep 5
      $0 start
      ;;
    *)
      echo "Usage $0 {start|stop|restart}" >&2
      exit 1
      ;;
esac
}

main $1
echo DONE

exit 0

