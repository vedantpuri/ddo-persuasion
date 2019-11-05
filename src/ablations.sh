#!/bin/bash

# Console text preferences
underline="$(tput smul)"
bold="$(tput bold)"
normal="$(tput sgr0)"
divider="=============================="

curr_dir=$(pwd)
# echo "${curr_dir}"
for file in "${curr_dir}/configs"/*
do
  echo -e "${divider}"
  echo "${bold}${file##*/}${normal}"
  python main.py ${file}
  echo -e "${divider}\n"
done
