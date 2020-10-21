import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUX_CLIENT_URL = os.environ['INFLUX_CLIENT_URL']
INFLUX_TOKEN = os.environ['INFLUX_DB_TOKEN']
INFLUX_ORG = os.environ['INFLUX_ORG']
INFLUX_BUCKET = os.environ['INFLUX_BUCKET']

influx_client = InfluxDBClient(url=INFLUX_CLIENT_URL, token=INFLUX_TOKEN)
influx_write_api = influx_client.write_api(write_options=SYNCHRONOUS)


def write_to_influx(data):
    influx_write_api.write(INFLUX_BUCKET, INFLUX_ORG, data)


def panel_info_to_influx_points(panel_info):
    points = []

    for control in panel_info['controls']:
        point = Point("cellar_panel_read")
        point.tag("slot", control["slot"])
        point.tag("vessel", control["label"])
        point.tag("batch_number", control['batch_info']['Batch #'])
        point.field("temp", control['temp'])
        point.field("set_point", control['set_point'])
        point.field("valve_open", control['valve_open'])
        point.field("days_in_vessel", control['batch_info']['Days in Vessel'])
        point.time(panel_info['read_at'], WritePrecision.NS)
        points.append(point)

    return points