#!/bin/sh
# wait-for-it.sh
#
# Usage:
#   wait-for-it.sh host:port [-s] [-t timeout] [-- command args...]
#
#   -s | --strict               Only execute command if the test succeeds
#   -t TIMEOUT | --timeout=TIMEOUT
#                               Timeout in seconds, zero for no timeout
#   -- COMMAND ARGS...          Execute command with args after the test finishes

TIMEOUT=15
STRICT=0
COMMAND=""

while [ $# -gt 0 ]
do
    case "$1" in
        *:* )
        HOST=$(printf "%s\n" "$1"| cut -d : -f 1)
        PORT=$(printf "%s\n" "$1"| cut -d : -f 2)
        shift 1
        ;;
        -s | --strict)
        STRICT=1
        shift 1
        ;;
        -t)
        TIMEOUT="$2"
        if [ "$TIMEOUT" = "" ]; then break; fi
        shift 2
        ;;
        --timeout=*)
        TIMEOUT="${1#*=}"
        shift 1
        ;;
        --)
        shift
        COMMAND="$@"
        break
        ;;
        *)
        echo "Unknown argument: $1"
        exit 1
        ;;
    esac
done

if [ "$HOST" = "" ] || [ "$PORT" = "" ]; then
    echo "Error: you need to provide a host and port to test."
    exit 1
fi

wait_for() {
    for i in `seq $TIMEOUT` ; do
        nc -z "$HOST" "$PORT" > /dev/null 2>&1
        result=$?
        if [ $result -eq 0 ] ; then
            if [ -n "$COMMAND" ] ; then
                exec $COMMAND
            fi
            exit 0
        fi
        sleep 1
    done
    echo "Operation timed out" >&2
    exit 1
}

wait_for

if [ -n "$COMMAND" ] ; then
    if [ $STRICT -eq 1 ] && [ $result -ne 0 ] ; then
        echo "Strict mode: command not executed" >&2
        exit 1
    fi
    exec $COMMAND
fi