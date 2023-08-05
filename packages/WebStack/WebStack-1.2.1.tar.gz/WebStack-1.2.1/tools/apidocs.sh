#!/bin/sh

epydoc --docformat=plaintext -o apidocs WebStack/Generic.py WebStack/Resources/*.py WebStack/Helpers/*.py WebStack/Repositories/*.py
