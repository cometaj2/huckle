#!/bin/bash

shopt -s expand_aliases
huckle pull https://hcli.io/hcli-webapp/cli/jsonf?command=jsonf
. ~/.huckle/huckle_profile   
echo {"hello":"world"} | jsonf go
