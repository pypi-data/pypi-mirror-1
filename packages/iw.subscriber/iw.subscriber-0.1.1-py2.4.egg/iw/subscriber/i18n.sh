#!/bin/sh
i18nextract -d iw.subscriber -d iw.subscriber -p .

i18ndude merge --pot locales/iw.subscriber.pot --merge iw.subscriber.pot

i18ndude sync --pot locales/iw.subscriber.pot $(find locales -name '*.po')

PO_FILES=$(find locales -type f -name '*.po')

for PO in ${PO_FILES}
do
    DIR=$(dirname ${PO})
    BASE=$(basename ${PO} ".po")
    echo -n ${PO}":"
    msgfmt -v -c -o ${DIR}/${BASE}.mo ${PO}
done
mv locales/iw.subscriber-fr.mo locales/fr/LC_MESSAGES/iw.subscriber.mo
