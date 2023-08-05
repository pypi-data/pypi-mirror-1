#!/bin/sh

find -name '*.pyc' -exec rm -fv '{}' ';'
find -name '*~' -exec rm -fv '{}' ';'

rm -fv httpd.conf
rm -fv logs/*
