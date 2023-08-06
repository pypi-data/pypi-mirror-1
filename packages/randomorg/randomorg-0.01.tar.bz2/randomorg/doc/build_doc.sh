#!/bin/sh
# vim: set sw=4 et sts=4 tw=80 :
# Copyright 2008 Ali Polatel <polatel@itu.edu.tr>
# Distributed under the terms of the GNU General Public License v3 

MODULE="randomorg"
CONFIG_FILE="doc/epydoc-randomorg.ini"
OUT_DIR="${HOME}/htdocs/blog/projects/randomorg"

epydoc --config="${CONFIG_FILE}" -o ${OUT_DIR} ${MODULE}
