#!/bin/bash



for d in */;
do
     (cd "$d" && echo "$d" && timeout 960 python3 check.py > raw_results.txt)
done
