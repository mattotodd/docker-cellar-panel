import { updateSetPoint } from "../../utils/cellar-helper";

export default function handler(req, res) {
	// gte these from request
	const body = JSON.parse(req.body);
	updateSetPoint(body.param).then(() => {
	  	res.statusCode = 200
	  	res.setHeader('Content-Type', 'application/json')
		res.end(JSON.stringify({ name: 'John Doe' }))
	});
}