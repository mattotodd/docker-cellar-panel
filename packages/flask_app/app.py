import os
import json
import atexit

from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

from cellar import default_dt, get_panel_information, read_and_store_cellar_panel, set_control
from cellar.google import get_sheet_values
from cellar.aws import record_cloudwatch_metric
from cellar import cache


app = Flask(__name__)


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

@app.route('/test_aws_metric')
def test_aws_metric():
    record_cloudwatch_metric()
    return "written"


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=read_and_store_cellar_panel, trigger="interval", seconds=60)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    
    app.run(debug=os.environ.get('DEBUG', 0) == '1', host='0.0.0.0', use_reloader=False)