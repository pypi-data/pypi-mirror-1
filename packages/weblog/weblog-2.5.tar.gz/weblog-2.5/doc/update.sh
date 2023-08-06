#!/bin/ksh

dst=${DST:-"${HOME}/henry.precheur.org/weblog/"}

if [[ -d $dst ]]; then
        ${HOME}/env/sphinx/bin/sphinx-build -b html -E . $dst || echo 'Error'
else
        echo "$dst doesn't exist"
fi
