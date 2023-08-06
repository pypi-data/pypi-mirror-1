#!/bin/sh

# UTILIZZO:
# Basta mettere questo script nella root del proprio prodotto e creare una serie di 
# folder locales/en/LC_MESSAGES, locales/fr/LC_MESSAGES, ecc dentro locales per ogni lingua
# con dei redomino.contact.po vuoti (o con l'intestazione). Se li crei vuoti abbi cura di modificare coerentemente
# l'intestazione (lingua e dominio)
# Modifica la variabile PRODUCTNAME e lancia lo script automatico. Dovrai solo tradurre le singole voci

# utile se ho un nuovo pot e voglio fare un merge
#i18ndude merge --pot locales/redomino.contact.pot --merge redomino.contact.pot

PRODUCTNAME='italianskin.tool'

i18ndude rebuild-pot --pot locales/${PRODUCTNAME}.pot --create ${PRODUCTNAME} .

i18ndude sync --pot locales/${PRODUCTNAME}.pot locales/*/LC_MESSAGES/${PRODUCTNAME}.po

# Compile po files
for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do
    if test -d $lang/LC_MESSAGES; then
        msgfmt -o $lang/LC_MESSAGES/${PRODUCTNAME}.mo $lang/LC_MESSAGES/${PRODUCTNAME}.po
    fi
done

OTHER_DOMAINS=""
# Compile po files
for other_domain in $OTHER_DOMAINS; do
    i18ndude sync --pot locales/${other_domain}.pot locales/*/LC_MESSAGES/${other_domain}.po
    for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do
        if test -d $lang/LC_MESSAGES; then
            msgfmt -o $lang/LC_MESSAGES/${other_domain}.mo $lang/LC_MESSAGES/${other_domain}.po
        fi
    done
done

