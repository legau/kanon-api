#!/bin/bash

count=0
until [[ $(curl -f -s http://localhost:8000/health) ]] || [[ $count -ge 20 ]];
do
	sleep 1
	((count++))
done
curl -f http://localhost:8000/health
