recent_stats = []
chart = null;

function receive_event(data) {
        console.log(data);
	//collect the 10 most recent data points
	//recent_stats.push(data['bandwidth']);
	//if (recent_stats.length > 10) {
//		recent_stats = recent_stats.slice(1);
//	}

	//print this to the div, later to a chart
//	chart = document.getElementById('chart');
//	chart.innerHTML = recent_stats;
}

function offline_driver() {
		var bw = Math.round(Math.random() * 200);
		var msgs = Math.round(Math.random() * 10000);

        message_event({'bandwidth':bw,'msgs':msgs});
        id=window.setTimeout ("offline_driver()", 1000);
}