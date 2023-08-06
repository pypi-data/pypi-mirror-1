#!/bin/bash
I18NDUDE="i18ndude"

if ! which $I18NDUDE > /dev/null; then
    echo "You need to install the $I18NDUDE utility first: easy_install $I18NDUDE"
    exit 1
fi

HELP="Syntax $0 domain"
if [ $# -lt 1 ]; then
       echo $HELP;
       exit 1
fi
          
# Access the real directory of the current file
cd -P `dirname $0`
PRODUCT_DIR="`dirname $PWD`"
PRODUCT=`basename $PRODUCT_DIR`
I18NDOMAIN=$1
POT=$I18NDOMAIN.pot
PO=$I18NDOMAIN.po
MANUAL=$I18NDOMAIN-manual.pot
LOG=rebuild.log

echo $PRODUCT_DIR;
echo $PRODUCT;

echo -n "Rebuilding POT files, this can take a while..."

# Rebuild the main POT file
touch $POT;
if [ -f "$MANUAL" ]
    then
        $I18NDUDE rebuild-pot \
            --pot $POT \
            --create $I18NDOMAIN \
            --merge $MANUAL \
            $PRODUCT_DIR  > $LOG 2>&1
    else 
        $I18NDUDE rebuild-pot \
            --pot $POT \
            --create $I18NDOMAIN \
            $PRODUCT_DIR  > $LOG 2>&1
fi


# Made paths relative to the product directory
sed -n "s,$PRODUCT_DIR,\.,g" $POT

echo " done. Full report at $LOG."

echo "Now updating the PO files:"

# Proceed with the PO syncing

for FILE in $( find $PRODUCT_DIR/locales -type f -name "*.po" ); do 
     # echo $FILE
     $I18NDUDE sync --pot $POT $FILE
done

