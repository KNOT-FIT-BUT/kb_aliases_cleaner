#!/bin/bash

test_cases=$(ls tests/)

for test_case in $test_cases
do
    name=$test_case
    out="/tmp/$test_case.out"
    test_case="tests/$test_case/$test_case"
    touch $out

    if [ "$1" = "-v" ]
    then
        ./start.sh "$(cat $test_case.flags)" --debug --input-file "$test_case.tsv" --output-file "$out"
    else
        ./start.sh "$(cat $test_case.flags)" --debug --input-file "$test_case.tsv" --output-file "$out" > /dev/null
    fi

    if ! [ "$?" = "$(cat $test_case.rc)" ]
    then 
        printf "[\e[31mFAIL\e[0m] %s : Wrong exit code\n" "$name"
        rm -f "$out"
        continue
    fi


    if ! [ "$(cat "$out" | xargs)" = "$(cat "$test_case.out" | xargs)" ]
    then 
        printf "$(cat -n "$out" | xargs)"
        printf "$(cat -n "$test_case.out" | xargs)"
        printf "[\e[31mFAIL\e[0m] %s : Output does not match\n" "$name"
        rm -f "$out"
        continue
    fi

    printf "[\e[32mPASS\e[0m] %s\n" "$name"
done
