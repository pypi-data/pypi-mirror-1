#!/bin/sh

apachectl -d $(pwd) -f httpd.conf -k stop
