#!/usr/bin/env python

import os
import shutil
import sys

if not os.path.isdir('tgquicktest'):
    os.mkdir('tgquicktest')

os.chdir('tgquicktest')

qs_variants = (
    ('SAIdentity', '-i -s'),
    ('SANoIdentity', '--no-identity -s'),
    ('SOIdentity', '-i -o'),
    ('SONoIdentity', '--no-identity -o'),
    ('ElIdentity', '-i -e'),
    ('ElNoIdentity', '--no-identity -e')
)

if len(sys.argv) > 1:
    choice = sys.argv[1]
else:
    choice = None

for variant, options in qs_variants:
    if choice and variant != choice:
        print "Skipping quickstart variant %s..." % variant
        continue
    try:
        if os.path.isdir(variant):
            shutil.rmtree(variant)
    except (OSError, IOError):
        print "Could not remove directory %s. Exiting..." % variant
        sys.exit(1)
    os.system('tg-admin quickstart %s -p %s %s' % (options, variant.lower(), variant))
    os.chdir(variant)
    os.system('python setup.py develop')
    os.system('python setup.py test')
    if '-i ' in options:
        os.system('bootstrap-%s -u test' % variant.lower())
    os.system('python start-%s.py'% variant.lower())
    raw_input("Hit ENTER to continue...")
    print
    os.chdir('..')

os.chdir('..')
