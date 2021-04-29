#!/bin/bash

count=0
until [[ $(curl -f -s http://localhost/health) ]] || [[ $count -ge 20 ]];
do
	sleep 1
	((count++))
done
curl -f http://localhost/health
