let stream_schema = {
	'quiz_uuid':'',
	'start':'',
	'end':'',
	'max_players':512
};

let streamQuiz = function (evt) {
	evt.preventDefault();

	stream_schema['quiz_uuid'] = $('#quiz_to_stream').val();
	stream_schema['start'] = $('#quiz_stream_start').val();
	stream_schema['end'] = $('#quiz_stream_end').val();
	stream_schema['max_players'] = parseInt($('#quiz_stream_players').val());

	$.ajax({
		url:'/l/api/stream-quiz',
		type: 'POST',
		data: stream_schema,
		dataType: 'json',
		success: function (resp) {
			if (!resp || resp.error === true) {
				_lancometer.apiErr(resp, 'Failed to create quiz stream!');
				return;
			}

			console.log(resp);
			if (resp.code) {
				location.reload();
			}
		},
		error: function (e) {
			_lancometer.apiErr(e, 'Failed to create quiz stream!');
		}
	});
};

$('#quiz_stream_form').on('submit', streamQuiz);
