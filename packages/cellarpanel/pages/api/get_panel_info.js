import { getPanelInfo } from "../../utils/cellar-helper";

export default function handler(req, res) {
	getPanelInfo().then((panelInfo) => {
	  	res.statusCode = 200
	  	res.setHeader('Content-Type', 'application/json')
		res.end(JSON.stringify(panelInfo))
	});
}