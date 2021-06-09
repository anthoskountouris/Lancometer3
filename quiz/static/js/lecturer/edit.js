let quiz_schema = {
	'name': '',
	'desc': '',
	'uuid': '',
	'type': 'relay',
	'questions': {}
};

let editQuiz = function (evt) {
	evt.preventDefault();

	quiz_schema['name'] = $('#editquiz_name').val();
	quiz_schema['desc'] = $('#editquiz_desc').val();
	quiz_schema['type'] = $('#editquiz_type').val();
	quiz_schema['uuid'] = $('#editquiz_uuid').val();

	$('#save_submit').text('Updating...');

	$.ajax({
		url: '/l/api/edit-quiz',
		type: 'POST',
		data: quiz_schema,
		dataType: 'json',
		success: function (resp) {
			if (!resp || resp.error === true) {
				_lancometer.apiErr(resp, 'Failed to load quiz information!');
				return;
			}
			$('#save_submit').text('Complete! Please wait...');

			window.location.href = '/l/manage-quiz';
		},
		error: function (e) {
			_lancometer.apiErr(e, 'Failed to load quiz information!');
			$('#save_submit').text('Error!');
		}
	})
};

$('#edit_quiz_form').on('submit', editQuiz);
