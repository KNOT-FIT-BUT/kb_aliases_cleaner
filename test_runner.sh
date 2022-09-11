#!/bin/bash

test_cases=$(ls tests/)

for test_case in $test_cases
do
    name=$test_case
    out="/tmp/$test_case.out"
    test_case="tests/$test_case/$test_case"
    touch $out

    ./start.sh "$(cat $test_case.flags)" --input-file "$test_case.tsv" --output-file "$out"

    if ! [ "$?" = "$(cat $test_case.rc)" ]
    then 
        printf "[\e[31mFAIL\e[0m] %s\n" "$name" ": Wrong exit code"
        rm -f "$out"
        continue;
    fi


    if ! [ "$(cat "$out" | xargs)" = "$(cat "$test_case.out" | xargs)" ]
    then 
        printf "[\e[31mFAIL\e[0m] %s\n" "$name" ": Output does not match"
        rm -f "$out"
        continue;
    fi

    printf "[\e[32mPASS\e[0m] %s\n" "$name"
done
