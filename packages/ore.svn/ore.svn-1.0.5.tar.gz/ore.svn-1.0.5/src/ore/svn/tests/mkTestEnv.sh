#!/bin/bash
bunzip2 testrepo.dump.bz2
svnadmin create testrepo
cat testrepo.dump | svnadmin load testrepo

