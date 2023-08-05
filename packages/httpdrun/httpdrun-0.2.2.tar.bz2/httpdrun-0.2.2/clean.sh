#!/bin/sh

find -name '*.pyc' -exec rm -fv '{}' ';'
find -name '*~' -exec rm -fv '{}' ';'

rm -rf build
rm -rf dist
