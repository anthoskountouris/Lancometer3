"use strict";

let version = 'v1:';
let appName = "lancometer"
let appLibraries = [
	// Font-awesome
	'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/solid.min.css',
	'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/fontawesome.min.css',
	// Bootstrap
	'https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.6.0/css/bootstrap.min.css',
	'https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.6.0/js/bootstrap.min.js',
	// jQuery
	'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js',
	// Leaflet
	'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.min.js',
	'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.min.css',
	'https://cdnjs.cloudflare.com/ajax/libs/leaflet-locatecontrol/0.73.0/L.Control.Locate.min.js',
	'https://cdnjs.cloudflare.com/ajax/libs/leaflet-locatecontrol/0.73.0/L.Control.Locate.min.css',
	// Chart.js
	'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.2.0/chart.min.js',
	// Sortable.js
	'https://cdnjs.cloudflare.com/ajax/libs/Sortable/1.13.0/Sortable.min.js'
];

let appStatic = [
	// Landing page
	'/lancometer/home',
	'/lancometer/privacy',
	'/lancometer/terms',

	// Important game pages
	'/entry',
	'/game',
	'/game/settings',
	'/login',

	'/static/images/logo.png',

	// CSS
	'/static/css/base.css',
	'/static/css/common.css',
	'/static/css/landing_page.css',
	'/static/css/loginregister.css',
	'/static/css/terms_and_privacy.css',

	// Play page JS
	'/static/js/play/api.js',
	'/static/js/play/game.js',
	'/static/js/play/ui.js',

	// Lecturer dashboard JS
	'/static/js/lecturer/create.js',
	'/static/js/lecturer/edit.js',
	'/static/js/lecturer/streams.js',

	// Main code
	'/static/js/service-worker.js',
	'/static/js/uploads.js',
	'/static/js/lancometer.js',
	'/static/js/main.js'
];

let appAssets = [].concat(appLibraries, appStatic);

self.addEventListener("install", function (event) {
	self.skipWaiting();

	event.waitUntil(caches.open(version + appName).then(function (cache) {
		return cache.addAll(appAssets);
	}).then(function () {
		console.log('sw: install completed');
	}));
});

self.addEventListener("fetch", function (event) {
	console.log('sw: fetch event in progress.');

	if (event.request.method !== 'GET') {
		console.log('sw: fetch event ignored.', event.request.method, event.request.url);
		return;
	}

	event.respondWith(
		caches.match(event.request).then(function (cached) {
			let networked = fetch(event.request).then(fetchedFromNetwork, unableToResolve).catch(unableToResolve);

			console.log('sw: fetch event', cached ? '(cached)' : '(network)', event.request.url);
			return cached || networked;

			function fetchedFromNetwork(response) {
				let cacheCopy = response.clone();
				console.log('sw: fetch response from network.', event.request.url);
				caches.open(version + 'pages').then(function add(cache) {
					cache.put(event.request, cacheCopy);
				}).then(function () {
					console.log('sw: fetch response stored in cache.', event.request.url);
				});
				return response;
			}

			function unableToResolve() {
				console.log('sw: fetch request failed in both cache and network.');
				return new Response('<h1 style="font-weight:100;font-family:sans-serif;">Lancometer3 Unavailable</h1>', {
					status: 503,
					statusText: 'Service Unavailable',
					headers: new Headers({
						'Content-Type': 'text/html'
					})
				});
			}
		})
	);
});

self.addEventListener("activate", function (event) {
	event.waitUntil(
		caches.keys().then(function (keys) {
			return Promise.all(
				keys.filter(function (key) {
					return !key.startsWith(version);
				}).map(function (key) {
					return caches.delete(key);
				})
			);
		}).then(function () {
			console.log('sw: activate completed.');
		})
	);
});
