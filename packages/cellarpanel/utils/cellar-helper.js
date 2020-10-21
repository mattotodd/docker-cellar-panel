const http = require("http");

const pages = [1, 2];

function wait(ms) {
    var start = Date.now(),
        now = start;
    while (now - start < ms) {
      now = Date.now();
    }
}

function fetchRetry(url, options, count) {
  count = (count) ? count : 1;
  // Return a fetch request
  return fetch(url, options).then(res => {
    // check if successful. If so, return the response transformed to json
    if (res.ok) return res.json()
    // else, return a call to fetchRetry
	count++;
	if (count > 5) {
		throw Exception('errrrr')
	}
    return fetchRetry(url, count)
  })
}

export function updateSetPoint(param) {
	return new Promise ((resolve, reject) => {
		const update_url = `http://cellar-service:5000/set_control_setpoint/${param}`;

		fetchRetry(update_url, {
			method: 'POST',
			body: '{}'
		}).then((panel_info) => {
			resolve(panel_info);
		});

		// http://10.1.10.105/submit.html?dummy=1603071188070o3a117t2v342

	});
}

export function getPanelInfo(tank_id) {
	return new Promise ((resolve, reject) => {
		const page_url = "http://cellar-service:5000/read_cellar_panel";
		fetchRetry(page_url).then((panel_info) => {
			resolve(panel_info);
		});
	});
}

