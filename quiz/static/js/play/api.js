let _api = {

	base: '/api/',
	timeout: 20000,

	init: function(){
		_api.prepareAjax();
	},

	prepareAjax: function (){
		$.ajaxSetup({
			cache: false,
			timeout: _api.timeout,
			beforeSend: function(xhr, settings) {
				if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
					xhr.setRequestHeader("X-CSRFToken", _csrf);
				}
			},
			error: _api.requestError
		});
	},

	requestError: function (e, msg) {
		console.error(e);
		if (!navigator.onLine) {
			_ui.popToastMessage('You are not online!', 5000);
		}
		_ui.popToastMessage(msg + ' ' + (e.statusText || 'Unknown API error'), false);
	},

	request: function (url, data = {}, successCallback, errorCallback) {
		$.ajax({
			url: _api.base + url,
			data: data,
			type: 'GET',
			dataType: 'json',
			timeout: _api.timeout,
			success: function(resp) {
				if (!resp){
					_api.requestError({}, 'Unknown error!');
				} else {
					if (resp.error === true) {
						_api.requestError({}, resp.message);
					} else {
						successCallback(resp);
					}
				}
			}
		});
	}

};
