#!/usr/bin/env bash
# Script to build wheel for BmCS package
# Directories are hardcoded in commands below. Must be edited to work on your computer
rm -r build
rm -r dist
python setup.py bdist_wheel
cp -r dist ../BmCS_installation_env
