#This script must be executed from the product folder.
#i18ndude should be available in current $PATH

echo Rebuilding pot...
i18ndude rebuild-pot --pot locales/collective.ui.ie6nomore.pot --create collective.ui.ie6nomore \
               --merge locales/collective.ui.ie6nomore.manual.pot *

for file in `find locales -name *.po`
do
    echo Syncing $file ...
    i18ndude sync --pot locales/collective.ui.ie6nomore.pot $file

    msgfmt -o `dirname $file`/`basename $file .po`.mo $file --no-hash
done

