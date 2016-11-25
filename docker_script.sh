#/bin/bash

# read the options
while getopts ":i::r::b:" opt; do
    case $opt in
        i)
            INPUT=$OPTARG
            ;;
        r)
            REFERENCE=$OPTARG
            ;;
        b)
            DB=$OPTARG
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            exit 1
            ;;
    esac
done

xvfb-run CanSNPer -i $INPUT -r $REFERENCE -b $DB -d

