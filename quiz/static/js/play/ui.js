/*
	Defines functions for use in the game UI
*/

let _ui = {

	freshToast: function ($toastBody, autohide, type = '') {
		let toastOpts = {
			'class': 'toast mx-5',
			'role': 'alert',
			'aria-live': 'polite',
			'aria-atomic': true
		};

		if (!!autohide) {
			toastOpts['data-autohide'] = !!autohide;
			toastOpts['data-delay'] = autohide;
		}

		return $("<div/>", toastOpts).append(
			$("<div/>", {
				'class': 'toast-header'
			}).append(
				$("<strong/>", {
					'class': 'me-auto text-primary'
				}).text('Message'),
				$('<small/>', {
					'class': 'text-muted'
				}),
				$('<button/>', {
					'type': 'button',
					'class': 'btn-close',
					'data-dismiss': 'toast',
					'aria-label': 'close'
				})
			),
			$toastBody
		).toast('show')
	},

	freshToastSmall: function ($toastBody, autohide, type) {
		return $("<div/>", {
			'class': 'toast mx-5 align-items-center' + type,
			'role': 'alert',
			'aria-live': 'assertive',
			'aria-atomic': true,
			'data-autohide': true,
			'data-delay': autohide
		}).append(
			$("<div/>", {
				'class': 'd-flex'
			}).append(
				$toastBody,
				$('<button/>', {
					'type': 'button',
					'class': 'btn-close me-2 m-auto',
					'data-dismiss': 'toast',
					'aria-label': 'close'
				})
			)
		).toast('show')
	},

	popToastMessage: function (txt, autohide, small = false, type = 'primary') {
		let $toastBody = $('<div/>', {
			'class': 'toast-body'
		}).text(txt);

		let typeText = ' text-white border-0 bg-' + type;
		let func = small ? _ui.freshToastSmall : _ui.freshToast

		$('#toast_alerts').append(func($toastBody, autohide, typeText));

		// Delete the toasts once they have served their purpose
		setTimeout(function () {
			console.log('removing', txt);
			let tt = $('#toast_alerts').find('.toast:not(.pendingremoval)').first();
			tt.addClass('pendingremoval').fadeOut(500);
			console.log(tt.text());
			setTimeout(function () {
				tt.remove();
			}, 500);
		}, autohide + 500);
	}

};
