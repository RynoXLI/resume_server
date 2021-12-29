#!/bin/bash

CONFIG_PATH=/home/steam/.config/unity3d/IronGate/Valheim/Midgard/valheim_server.log
TIME=`date +"%Y-%m-%d %H:%M:%S"`
CONNECTIONS=`grep -E "(Connections).+(ZDOS)" $CONFIG_PATH | tail -1 | awk '{print $4}'`

echo "$TIME Players Online: $CONNECTIONS"

INSTANCE=`wget -qO- --header="Content-Type:application/json"  http://169.254.169.254/latest/meta-data/instance-id`

echo "$TIME Instance-id: $INSTANCE"


if [[ $CONNECTIONS = "0" ]]; then
echo "$TIME Shutting down server"
aws ec2 stop-instances --instance-ids $INSTANCE
fi
