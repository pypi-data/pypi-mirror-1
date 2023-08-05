#!/bin/sh

if [ -z "$1" ]; then
    echo "usage: $0 user"
    exit 1
fi

ipcs -s | grep $1 | perl -e 'while (<STDIN>) { @a=split(/\s+/); print `ipcrm sem $a[1]`}'
