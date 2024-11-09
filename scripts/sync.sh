#!/usr/bin/env bash
cd "$(dirname "$0")"
if [ -n "$code" ]; then
	sudo cp ./*.py $code/scripts/
fi
