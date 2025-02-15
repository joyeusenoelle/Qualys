# encoding: utf-8
#-
# Source URL: https://github.com/SBB-Mx/Qualys
#

#-
# "Fix" for Self-signed certificates in chain.
# Does this actually work?  Should we just remove it?
#
import ssl

try:
	_create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
# Legacy Python that doesn't verify HTTPS certificates by default
	pass
else:
# Handle target environment that doesn't support HTTPS verification
	ssl._create_default_https_context = _create_unverified_https_context

#-
# Original Script
# Edited by Noëlle Anthony 7/28/2022
#

import argparse, sys
from datetime import datetime, timedelta
import logging

from lxml import objectify
import qualysapi 

logging.basicConfig()
logger = logging.getLogger('logger')

class QualysError(Exception):
	pass

def create_attributes_dict(host):
	"""Create and return a dictionary of important attributes and values associated
	with them. The key of each dictionary entry is the attribute; the value is
	a tuple composed of:
	* identifier text for the attribute, meant to be printed to output before its value;
	* error text for the attribute, meant to be printed to output if the attribute isn't present;
	* a boolean determining whether to write the attribute to the CSV.
	"""
	impt_attrs = {
		host.get("ID", None): ("ID", "No ID!", False),
		host.get("IP", None): ("IP", "No IP!", True),
		host.get("DNS", None): ("DNS", "No DNS!", True),
		host.get("OS", None): ("OS", "No OS!", False),
		host.get("LAST_VULN_SCAN_DATETIME", None): ("Last day scanned", "No last day scanned!", True),
		host.get("ASSET_GROUP_IDS", None): ("Asset group", "No Asset group!", False),
	}
	return impt_attrs

def get_data(days):
	try:
		a = qualysapi.connect('config.ini')
		assets = a.request('/api/2.0/fo/asset/host/',{
			'action':'list',
			'details':'All/AGs',
			'no_vm_scan_since':days,
			'use_tags':'1',
			'tag_set_by':'name',
			'tag_include_selector':'any',
			'tag_set_include':'[Any_Tag_here]',
			},verify=False)  # Prevent 'Self-Signed Certificate in Chain' from blocking activity
		
		root = objectify.fromstring(assets.encode('utf-8'))
		with open("ips.csv","w+") as ips_file:
			output_list = []
			output_list.append("*** Query Data ***")
			output_list.append("IP, DNSHostname, LastScanDate")
			for host in root.RESPONSE.HOST_LIST.HOST:
				impt_attrs = create_attributes_dict(host)
				inner_output_list = []
				print("\n++++++++++++++++++++++++++++++++++++++++\n")
				# woo tuple destructuring!
				# The dictionary has host.WHATEVER as keys, and then as values,
				# a tuple of (print_text, error_text, write_to_csv). Python
				# allows us to destructure that tuple into individual variables
				# in place, with the parentheses and commas. In fact, that's what
				# we're doing with the return from impt_attrs.items() - it
				# returns a tuple, which we're destructuring into attr and the
				# inner tuple that we need to destructure separately.
				# (Why are we doing this at all? Don't Repeat Yourself. We 
				# don't need all that repeated print() / if AttributeError / etc.
				# code when a simple loop will do.)
				for attr, (p_text, e_text, write_to_csv) in impt_attrs.items():
					try:
						print(f"{p_text}: {attr.text}")
						if write_to_csv:
							inner_output_list.append(attr.text)
					except AttributeError:
						print(f"{e_text}")
						if write_to_csv:
							inner_output_list.append(e_text)
				print(f"\n++++++++++++++++++++++++++++++++++++++++\n")
				inner_output = ",".join(inner_output_list)
				output_list.append(inner_output)
			output = "\n".join(output_list)
			file.write(output)
			
	except AttributeError:
		raise QualysError(f"I can't find any data for hosts not scanned since {days}.")	


# WHAT DOES THIS DO?
# Moving the main logic of the file into a function lets you import it into
# other Python scripts without automatically running all of this script's logic
# below. Now it only runs if you call the main() function...
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("days", type=int, help="The number of days back to scan")
	args = parser.parse_args()

	print ("*** Query Data ***")

	day = (datetime.today()  - timedelta(days=args.days)).strftime('%Y-%m-%d')
	print(f"Scanning back to: {day}")
	get_data(day)

# ...and this calls the main() function if you're running it from the command
# line (or by double-clicking it, if you're on some weird not-Linux system).
# It only runs if this is the primary (__main__) script running.
if __name__ == "__main__":
	main()
