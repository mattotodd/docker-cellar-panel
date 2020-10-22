import os
import re
import time
import json
import requests
from datetime import date, datetime 

from .influxdb import write_to_influx, panel_info_to_influx_points

from cellar import cache
from cellar import google

CELLAR_PANEL_IP = os.environ['CELLAR_PANEL_IP']

PAGES = [1, 2]

ADDRESSES = [117, 118, 119, 120, 121, 122, 123, 124, 125] # only marking the ones we use 1-9
LABELS = [
	'FV 10/1', 
	'FV 10/2', 
	'FV 10/3', 
	'FV 10/4', 
	'FV 10/5',
	'FV 10/6',
	'FV 20/1',
	'Walk-In',
	'BT 10/1'
]


def default_dt(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()


def find_double_quoted_strings(text):      
	matches=re.findall(r'\"(.+?)\"', text)
	return matches


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start


def get_panel_values():
	values = []
	for page in PAGES:
		page_html = read_panel_html(page)
		values.extend(panel_html_to_values(page_html))
		time.sleep(1)

	return values


def convert_to_float(val):
	try:
		return float(val)
	except:
		print("error in conversion")
		return None


def get_panel_information():
	previous_info = cache.LAST_READING


	values  = get_panel_values()
	now = datetime.utcnow()

	# new info
	panel_info = {'read_at': now, 'controls': []}

	# read production info
	production_info = []
	try:
		# go get the most recent 25 rows
		production_info = google.get_sheet_values(limit=25)
	except:
		pass

	for idx, address in enumerate(ADDRESSES):
		control_id = idx+1
		control_label = LABELS[idx]
		control = {
			'address': int(address),
			'slot': int(control_id),
			'label': control_label,
			'temp': convert_to_float(values[0+(idx*3)]),
			'set_point': convert_to_float(values[1+(idx*3)]),
			'valve_open': 1 if values[2+(idx*3)] == '1' else 0,
		}

		# attempt to get batch info from production_info data
		batch_info = next((r for r in production_info if r['Vessel'] == control_label), None)

		# if not found in production_info - see if we have it cache from previous read
		if batch_info is None and previous_info:
			batch_info = next((c['batch_info'] for c in previous_info['controls'] if c['label'] == control_label), None)
			batch_info['Days in Vessel'] = 0

		# if still not found - set blank dict info
		if batch_info is None:
			batch_info = {k:'' for k in ['Batch #', 'Split', 'Beer', 'Date Brewed', 'Batch Size', 'Vessel', 'Actual Volume', 'OG', 'FG', 'Notes', 'Packaged 1/6bbl', 'Packaged 1/2bbl', 'Packaged Cases 16oz']}
			batch_info['Batch #'] = 0
			batch_info['Days in Vessel'] = 0


		# calc days in vessel
		try:
			if batch_info['Date Brewed']:
				batch_info['Days in Vessel'] = (now - datetime.strptime(batch_info['Date Brewed'], '%m/%d/%Y')).days
		except:
			batch_info['Days in Vessel'] = 0

		control['batch_info'] = batch_info

		panel_info['controls'].append(control)
	cache.LAST_READING = panel_info
	return panel_info


def panel_html_to_values(tank_html):
	begin_tag = "<Script>"
	begin_idx = find_nth(tank_html, begin_tag, 2) + len(begin_tag)

	remaining_text = tank_html[begin_idx:]

	end_tag = "</Script>"
	end_idx = find_nth(remaining_text, end_tag, 1) + len(end_tag)

	remaining_text = remaining_text[0:end_idx]

	lines = remaining_text.splitlines()

	for line in lines:
		line = line.strip()
		if line.startswith('var V ='):
			# current values
			values = find_double_quoted_strings(line)
			return values


def read_panel_html(page):
	resp = requests.get(f"http://{CELLAR_PANEL_IP}/00{page}.html")
	return resp.text


def set_control(param):
	submit_url = f"http://{CELLAR_PANEL_IP}/submit.html?dummy={param}"
	print(submit_url)
	resp = requests.get(submit_url)
	if resp.status_code == 200:
		# clear cached values
		cache.LAST_READING = None
	return resp.text


def read_and_store_cellar_panel():
	info = get_panel_information()
	points = panel_info_to_influx_points(info)
	write_to_influx(points)

