#!/usr/bin/env python

#This script handles updates of the 'collective.portlet.facet' i18n domain
#You need to have i18ndude in your system path to run it

import subprocess, sys, os

DOMAIN = 'collective.portlet.facet'
PRODUCT = 'collective.portlet.facet'

def generate():
    command = "i18ndude rebuild-pot --pot i18n/generated.pot --create %s ." % (DOMAIN)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    print p.stdout.read()

def merge():
    print "Merging manual entries"
    command = "i18ndude merge --pot i18n/generated.pot --merge i18n/manual.pot"
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    print p.stdout.read()

def sync():
    print "Syncing i18n files"
    command = "i18ndude sync --pot i18n/generated.pot i18n/collective.portlet.facet*.po"
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    print p.stdout.read()

generate()
#merge()
sync()
print 'All done'