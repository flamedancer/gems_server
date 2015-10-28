#!/bin/bash

DIR=$(dirname $(readlink -f $0))
./pvp_stop.sh


echo "restart"
#!/bin/bash
ports=(9081)
for port in ${ports[@]}
do
    nohup python -u ${DIR}/realtime_pvp/pvp.py "${port}" >> ${DIR}/logs/realtime_pvp.log 2>&1  &
done
echo `ps aux|grep $DIR/realtime_pvp/pvp.py`
