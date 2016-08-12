#!/bin/bash

for i in `find src/ -name *.txt` 
do
	echo -e "$i"
	iconv -c -f UTF-16LE -t UTF-8 $i -o /tmp/iconv.tmp 
	mv /tmp/iconv.tmp $i 
done

