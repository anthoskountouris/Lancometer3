let csrf = $('#csrf_token').data('value');

let _lancometer = {

	_csrf: $('#csrf_token').data('value'),
	_notifs:[],

	init: function () {
		_lancometer.setupOffline();
		_lancometer.setupAjax();
	},

	setupOffline: function () {
		if ('serviceWorker' in navigator) {
			navigator.serviceWorker.register('/static/js/service-worker.js').then(function (reg) {
				console.log('ServiceWorker registration successful with scope: ', reg.scope);
			}, function (e) {
				console.log('ServiceWorker registration failed: ', e);
			});
		}
	},

	setupAjax: function () {
		_lancometer._csrf = $('#csrf_token').data('value');

		$.ajaxSetup({
			cache: false,
			timeout: 25000,
			beforeSend: function (xhr, settings) {
				if (!this.crossDomain) {
					if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
						xhr.setRequestHeader("X-CSRFToken", _lancometer._csrf);
					}
				}
			}
		});
	},

	genRandomId: function (length) {
		let result = '',
			characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_';
		let charactersLength = characters.length;
		for (let i = 0; i < length; i++) {
			result += characters.charAt(Math.floor(Math.random() * charactersLength));
		}
		return result;
	},

	apiErr: function (e, msg) {
		// TODO: Write an alert function to create a modal that better fits our design
		console.error(e);
		if (e.status && e.status === 429) {
			alert('You are performing actions too quickly!');
			return;
		}
		if (e.statusText && e.statusText === 'abort') {
			alert('Request cancelled by user action');
			return;
		}
		if (!navigator.onLine) {
			alert('You are not online.')
		}
		alert(msg + ' ' + (e.statusText || 'Unknown API error'));
	},

	notify: function (txt) {
		// Let's check if the browser supports notifications
		if (!("Notification" in window)) {
			return;
		}

		function makeNotification(txt) {
			_lancometer._notifs.push(
				new Notification('Lancometer3', {
					body:txt
				})
			);
		}

		if (Notification.permission === "granted") {
			makeNotification(txt)
		} else {
			Notification.requestPermission().then(function (permission) {
				if (permission === "granted") {
					makeNotification(txt);
				} else {
					console.error(permission);
				}
			});
		}
	}

}

_lancometer.init();

let copy = function(obj) {
	return JSON.parse(JSON.stringify(obj));
};

let getBaseLayer = function(){
	return new L.TileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}&hl=en',
		{
			attribution: '<a href="https://maps.google.co.uk" rel="noopener">Google Maps</a> | Lancometer 3.0',
			maxNativeZoom: 18,
			maxZoom: 20
		}
	);
};
