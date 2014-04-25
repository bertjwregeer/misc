#!/bin/sh

# files are named as such: <zonename>.conf where zonename might be: example.com

for I in *.zone; do 
	echo "zone:";
	echo "	name: \"${I/.zone/}\""; 
	echo "	zonefile: \"$I\""; 
done
