import os
import json
import atexit
# import logging
# import socket
# from datetime import datetime
# from logging.handlers import SysLogHandler

from flask import Flask, request, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

from cellar import default_dt, get_panel_information, read_and_store_cellar_panel, set_control
from cellar.google import get_sheet_values
from cellar import cache

DEBUG = os.environ.get('DEBUG', 0) == '1'


app = Flask(__name__)


# # LOGGING
# PAPERTRAIL_HOST = os.environ.get('PAPERTRAIL_HOST', None)
# PAPERTRAIL_PORT = os.environ.get('PAPERTRAIL_PORT', None)
# PAPERTRAIL_APP  = os.environ.get('PAPERTRAIL_APP', str(app))

# class ContextFilter(logging.Filter):
#     hostname = socket.gethostname()
#     def filter(self, record):
#         record.hostname = ContextFilter.hostname
#         return True

# logger = logging.getLogger()

# if not DEBUG and PAPERTRAIL_HOST and PAPERTRAIL_PORT:
#     syslog = SysLogHandler(address=(PAPERTRAIL_HOST, int(PAPERTRAIL_PORT)))
#     syslog.addFilter(ContextFilter())
#     format = f"%(asctime)s %(hostname)s {PAPERTRAIL_APP}: %(message)s"
#     formatter = logging.Formatter(format, datefmt='%b %d %H:%M:%S')
#     syslog.setFormatter(formatter)
#     logger = logging.getLogger()
#     logger.addHandler(syslog)
#     logger.setLevel(logging.INFO)
# # End Logging

# @app.after_request
# def after_request(response):
#     timestamp = datetime.now().strftime('%Y-%b-%d %H:%M')
#     app.logger.info('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
#     return response


@app.route('/read_cellar_panel')
def read_cellar_panel():
    if cache.LAST_READING is None:
        info = get_panel_information()
    else:
        info = cache.LAST_READING

    return app.response_class(
        response=json.dumps(info, default=default_dt),
        status=200,
        mimetype='application/json'
    )


@app.route('/set_control_setpoint/<param>', methods=['POST'])
def set_control_setpoint(param):
    set_control(param)
    return app.response_class(
        response=json.dumps({"ok": True}, default=default_dt),
        status=200,
        mimetype='application/json'
    )


@app.route('/prod_sheet')
def read_prod_info():
    resp = get_sheet_values()
    return app.response_class(
        response=json.dumps(resp, default=default_dt),
        status=200,
        mimetype='application/json'
    )


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=read_and_store_cellar_panel, trigger="interval", seconds=60)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    
    app.run(debug=DEBUG, host='0.0.0.0', use_reloader=False)