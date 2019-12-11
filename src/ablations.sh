#!/bin/bash
# ablations.sh
# Author: Vedant Puri
# Version: 1.1.0

# Console text preferences
underline="$(tput smul)"
bold="$(tput bold)"
normal="$(tput sgr0)"
divider="=============================="

# Script information
script_version="1.1.0"

# Environment info
curr_dir="$(pwd)/"
configs_dir="${curr_dir}configs"
output_file=""
data_path=""

# Print the script version to console
print_version() {
  echo "${script_version}"
}

# Print help message
print_usage() {
  echo -e "Usage: ${bold}./ablations.sh${normal} [-v] [-h] [-d /path/to/data] [-o *output_file*] [-f] [-c config1, config2]
  where:
  ${underline}-v${normal}        Prints script version
  ${underline}-h${normal}        Prints script usage
  ${underline}-c${normal}        Executes with specified config file  (REQUIRED) [\"all\" OR specific name OR comma separated list]
  ${underline}-o${normal}        Output file to save results to (REQUIRED)
  ${underline}-d${normal}        Path to the local DDO dataset files (REQUIRED)
  ${underline}-f${normal}        Flush output file if exists"
}

# Run all configs
run_all() {
  echo -e "Running all configurations\n"
  for file in "${configs_dir}"/*/*
  do
    python main.py "${data_path}" "${output_file}" "${file}"
  done
}


# Run directory
run_dir() {
  echo -e "Running directory routine for ${1#*=}\n"
  for file in "${configs_dir}/${1#*=}"/*
  do
    python main.py "${data_path}" "${output_file}" "${file}"
  done
}

# Run a specific config
run_specific() {
  [[ ! -f "${1}" ]] && echo "Specific Config File doesn't exit" && exit
  echo -e "Running ${1}\n"
  python main.py "${data_path}" "${output_file}" "${1}"

}

# Determine and run the configs
run_jobs() {
  jobs="${1}"
  # Run all
  [[ "${jobs}" == "all" ]] && run_all && return

  # Run specific directory of configs
  [[ "${jobs::3}" == "dir" ]] && run_dir "${jobs}" && return

  # Run a single specific config
  [[ "${jobs}" != *","* ]] && run_specific "${jobs}" && return

  # Run a list of comma separated configs [no space before/after comma]
  for i in $(echo $jobs | sed "s/,/ /g")
  do
      run_specific "$i"
  done
}

# Parse script arguments
parse_args() {
  while getopts ":hvfd:c:o:" opt; do
  case ${opt} in
    v)
    print_version
    ;;
    d)
    # set output file here
    data_path="${OPTARG}"
    ;;
    o)
    # set output file here
    output_file="${OPTARG}"
    ;;
    f)
    # if this option is present then flush output file if it exists
    [[ -f "${output_file}" ]] && rm "${output_file}"
    ;;
    h)
    print_usage
    ;;
    c)
    jobs=$OPTARG
    run_jobs "${jobs}"
    ;;
    \?)
    echo "Invalid argument. Run with ${underline}-h${normal} for help."
    ;;
    :)
    echo "Invalid argument. Run with ${underline}-h${normal} for help."
    ;;
  esac
done
}

parse_args "${@}"
