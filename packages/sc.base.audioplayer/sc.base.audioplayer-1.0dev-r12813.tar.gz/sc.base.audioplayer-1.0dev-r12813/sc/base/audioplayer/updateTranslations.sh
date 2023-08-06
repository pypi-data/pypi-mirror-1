#This script must be executed from the product folder.
#i18ndude should be available in current $PATH

echo Rebuilding pot...
i18ndude rebuild-pot --pot locales/sc.base.audioplayer.pot --create sc.base.audioplayer \
               --merge locales/sc.base.audioplayer.manual.pot *

for file in `find locales -name *.po`
do
    echo Syncing $file ...
    i18ndude sync --pot locales/sc.base.audioplayer.pot $file

    msgfmt -o `dirname $file`/`basename $file .po`.mo $file --no-hash
done

