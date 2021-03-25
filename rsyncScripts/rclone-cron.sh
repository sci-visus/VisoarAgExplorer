#!/bin/bash
if pidof -o %PPID -x “rclone-cron.sh”; then
exit 1
fi
rclone sync …
exit

#chmod a+x /path/rclone-cron.sh
#crontab -e
#0 0  * * * /path/rclone-cron.sh >/dev/null 2>&1