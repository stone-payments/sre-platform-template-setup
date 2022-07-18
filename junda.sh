#!/bin/sh

ls -lh

pwd

pipenv run python setup.py $1
