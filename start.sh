#!/bin/bash

usage() {
	echo "Usage $0 [ -h ][ -d ][ -k ][ -t THRESHOLD ][ --input-file FILE ][ --output-file FILE ]"
	echo "	-h - Prints out usage of program"
	echo "	-d - Start in debug mode (generate files like aliases.txt, aliases_match.tsv"
	echo "	-k - download the KB, disablexs PATH_TO_KB argument"
	echo "	-t THRESHOLD - set new threshold for filtering aliases (number of matches)"
	echo "	--input-file - set path to input KB (default is KB.tsv in current directory)"
	echo "	--output-file - set path to output KB (default is KB.tsv in current directory)"
}

DEBUG=""
PATH_KB=0
THRESHOLD=
PATH_TO_KB=unset
OUTPUT_FILE=unset
DOWNLOAD_KB=false

PARSED_ARGS=$(getopt -a -n run_filter_alias -o hkdt: --long input-file:,output-file: -- "$@")
VALID_ARGS=$?
if [ "$VALID_ARGS" != "0" ]; then
	usage
fi

eval set -- "$PARSED_ARGS"

while :
do
	case "$1" in 
		-h) usage exit	; shift	;;
		-k) DOWNLOAD_KB=true	; shift	;;
		-d) DEBUG="-d"	; shift	;;
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
	wget http://knot.fit.vutbr.cz/NAKI_CPK/NER_ML_inputs/KB/KB_cs/KB_cs_20200801-1597308491/KB.tsv &> /dev/null
	PATH_TO_KB="--input-file "$PWD"/KB.tsv"
elif [ "$DOWNLOAD_KB" == true ]; then
	echo "[*] Downloading the KB"
	if [ -e "KB.tsv" ]; then
		rm "KB.tsv"
	fi
	wget http://knot.fit.vutbr.cz/NAKI_CPK/NER_ML_inputs/KB/KB_cs/KB_cs_20200801-1597308491/KB.tsv &> /dev/null
	PATH_TO_KB="--input-file "$PWD"/KB.tsv"
fi

echo "[*] Starting filter_alias.py"
./filter_alias.py $DEBUG $THRESHOLD $PATH_TO_KB $OUTPUT_FILE
echo "[*] Cleaning up"
if [ -e "num_aliases.tsv" ]; then
	rm "num_aliases.tsv"
fi
if [ -e "namegen_gn_output.txt" ]; then
	rm "namegen_gn_output.txt"
fi
if [ -e "namegen_input.txt" ]; then
	rm "namegen_input.txt"
fi
