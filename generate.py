#!/usr/bin/ENV python
# coding: utf-8
"""
Generate faxes to send to list of addressees
"""
import csv
import os
import sys
from jinja2 import FileSystemLoader
from latex.jinja2 import make_env
from latex import build_pdf

if len(sys.argv) != 2:
    print "Provide the path to the file containing the text of the body of the faxes."
    print "e.g.> %s file.txt" % (sys.argv[0])
    sys.exit(1)

FAXPATH = sys.argv[1]
with open(FAXPATH, 'r') as myfile:
    FAXTEXT = myfile.read().replace('\n', '')

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
ENV = make_env(loader=FileSystemLoader("."))
TEMPLATE = ENV.get_template('fax.latex')

with open("sender.csv") as sendercsv:
    SENDER = csv.DictReader(sendercsv).next()

ADDRESSEES = []
with open("addressees.csv") as addressees:
    for entry in csv.DictReader(addressees):
        # Addresses are '|' delimited. Convert to latex newlines '\\'
        entry['addressee'] = "\\\\".join(entry['address'].split("|")) +\
                             "\\\\FAX: %s" % entry['fax_number']
        # Create a filename for this addressee
        entry['filename'] = entry['greeting'].lower().replace(' ', '_') + ".pdf"
        entry['signature'] = SENDER['signature_file']
        entry['faxtext'] = FAXTEXT
        entry['sendername'] = SENDER['name']
        entry['senderzip'] = SENDER['zip']
        entry['senderstate'] = SENDER['state']
        entry['sendercity'] = SENDER['city']
        entry['senderaddress'] = "\\\\".join([SENDER['address'], "%s, %s %s" %\
		                      (SENDER['city'], SENDER['state'], SENDER['zip']),\
							  "Email: " + SENDER['email'], "Phone: " + SENDER['phone']])
        entry['constituent'] = True if entry['constituent'] == 'True' else False
        ADDRESSEES.append(entry)

for addressee in ADDRESSEES:
    print "Writing fax to %s" % (addressee['greeting'])
    pdf = build_pdf(TEMPLATE.render(addressee), texinputs=[CURRENT_DIR, ''])
    pdf.save_to(FAXPATH + "." + addressee['filename'])
