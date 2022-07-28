#-
# Bulk delete Assets using CSV generated by listOlderAssets.py
#

import qualysapi 
import csv
from lxml import objectify


#-
# Initialize variables
#
file = "bulk_test.csv"

def build_dict(file):
   with open(file, newline='') as csvfile:
      reader = csv.DictReader(csvfile)


def action(build_dict):
   for row in reader:
      print('Submitting purge request for',row['IP'])

action(build_dict)

#-
# Connect with Qualys API, and submit Purge request into the queue
#

#def get_data(file):
#	try:
#		a = qualysapi.connect('config.ini')
#		assets = a.request('/api/2.0/fo/asset/host/',{
#         'action':'purge',
#         'data_scope':'pc,vm',
#			'ips':csv_in,
#			},verify=False)  # Prevent 'Self-Signed Certificate in Chain' from blocking activity
#	except AttributeError:
#		print("error", "Can't find the data")
      
      
      
      