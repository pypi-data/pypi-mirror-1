#!/bin/bash
MSGFMT="msgfmt"
if ! which $MSGFMT > /dev/null; then
    echo "error: missing $MSGFMT - install it first"
    exit 1
fi

for FILE in $(find `pwd` -type f -name "*.po" ); do
    DOMAIN=`basename $FILE .po`
    C_DIR=`dirname $FILE`
    msgfmt -o ${C_DIR}/${DOMAIN}.mo $FILE
done

