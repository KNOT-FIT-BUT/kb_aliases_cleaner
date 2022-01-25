#!/bin/bash

usage() {
	echo "Usage $0 [ -h ][ -d ][ -k ][ -t THRESHOLD ][ --input-file FILE ][ --output-file FILE ]"
	echo "	-h - Prints out usage of program"
	echo "	-k - download the KB, disablexs PATH_TO_KB argument"
	echo "	-t THRESHOLD - set new threshold for filtering aliases (number of matches)"
    echo "	--destoy - aliases are not marked but destroyed"
    echo "	--debug - Start in debug mode (generate files like aliases.txt, aliases_match.tsv)"
	echo "	--input-file - set path to input KB (default is KB.tsv in current directory)"
	echo "	--output-file - set path to output KB (default is KB.tsv in current directory)"
    exit 0
}

KB_URL=http://knot.fit.vutbr.cz/NAKI_CPK/NER_ML_inputs/KB/KB_cs/new/KB.tsv
DEBUG=""
DESTROY=""
PATH_KB=0
THRESHOLD=
PATH_TO_KB=unset
OUTPUT_FILE=unset
DOWNLOAD_KB=false

PARSED_ARGS=$(getopt -a -n run_filter_alias -o hkt: --long destroy,debug,input-file:,output-file: -- "$@")
VALID_ARGS=$?
if [ "$VALID_ARGS" != "0" ]; then
	usage
fi

eval set -- "$PARSED_ARGS"

while :
do
	case "$1" in 
		-h) usage; shift	;;
		-k) DOWNLOAD_KB=true	; shift	;;
		--destroy) DESTROY="--destroy"	; shift	;;
		--debug) DEBUG="--debug"	; shift	;;
		-t) THRESHOLD="-t "$2 ; shift 2	;;
		--input-file) PATH_TO_KB="--input-file "$2	; shift 2	;;
		--output-file) OUTPUT_FILE="--output-file "$2	; shift 2	;;
		--) shift; break;;
		*) echo "Unexpected option: $1" 
			usage
			exit 2;;
	esac
done

if [[ "$DOWNLOAD_KB" == true && $PATH_TO_KB != unset ]]; then
	echo "[!] -k argument set, ignoring PATH_TO_KB"
	echo "[*] Downloading the KB"
	if [ -e "KB.tsv" ]; then
		rm "KB.tsv"
	fi
	wget "$KB_URL" &> /dev/null
	PATH_TO_KB="--input-file "$PWD"/KB.tsv"
elif [ "$DOWNLOAD_KB" == true ]; then
	echo "[*] Downloading the KB"
	if [ -e "KB.tsv" ]; then
		rm "KB.tsv"
	fi
	wget "$KB_URL" &> /dev/null
	PATH_TO_KB="--input-file "$PWD"/KB.tsv"
fi

echo "[*] Starting filter_alias.py"
`dirname $0`/filter_alias.py $DEBUG $DESTROY $THRESHOLD $PATH_TO_KB $OUTPUT_FILE
echo "[*] Cleaning up"
if [ "DEBUG" = "" ]; then
	if [ -e "num_aliases.tsv" ]; then
		rm "num_aliases.tsv"
	fi
	if [ -e "namegen_gn_output.txt" ]; then
		rm "namegen_gn_output.txt"
	fi
	if [ -e "namegen_input.txt" ]; then
		rm "namegen_input.txt"
	fi
fi
