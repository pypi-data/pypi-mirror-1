#!/bin/bash
I18NDUDE="i18ndude"

if ! which $I18NDUDE > /dev/null; then
    echo "You need to install the $I18NDUDE utility first: easy_install $I18NDUDE"
    exit 1
fi

HELP="Syntax $0 lang-code (de, en, it etc.)"
if [ $# -lt 1 ]; then
       echo $HELP;
       exit 1
fi
          
PO=$I18NDOMAIN.po
LANG=$1
C_DIR=`pwd`

mkdir $C_DIR/$LANG
mkdir $C_DIR/$LANG/LC_MESSAGES

for POT in $( find $C_DIR -type f -name "*.pot" ); do 
    PO=$C_DIR/${LANG}/LC_MESSAGES/`basename $POT .pot`.po
    touch ${PO}_tmp
    $I18NDUDE sync --pot $POT ${PO}_tmp
    sed "s,Language-Code: en,Language-Code: $LANG,g" ${PO}_tmp > $PO
    rm ${PO}_tmp
done
