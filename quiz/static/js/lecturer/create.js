let quiz_schema = {
	'name': '',
	'desc': '',
	'type': 'relay',
	'questions': {}
};

let instructions = {
	'multiple_choice':'Specify multiple potential answers to your question and mark 1 or more as correct.',
	'map_choose':'Specify a location on a map and a radius in which correct answers will be accepted',
	//'keywords':'Create a list of keywords and '
	'answer_ranking':'Specify a list of items in the correct order, Lancometer will shuffle them and ask participants to re-order them',
	'organisation':'Organise words or phrases into categories similar to a venn diagram',
	'range_slider':'Specify minimum and maximum values as well as a step.'
};


let maps = {};
let map_circles = {};
let questions = {};

let setupLeafletMap = function(questionId) {
	maps[questionId] = L.map('__internal_map_chooser_id_' + questionId, {
		preferCanvas: true
	}).setView([52.5201508, -1.5807446], 10);

	L.control.scale().addTo(maps[questionId]);
	L.control.locate({
		position: 'topright',
		icon: 'fas fa-map-marker-alt'
	}).addTo(maps[questionId]);

	maps[questionId].addLayer(getBaseLayer());

	map_circles[questionId] = [];
	maps[questionId].on('click', function(evt){
		let latlng = Object.values(evt.latlng);
		console.log(evt);
		console.log(latlng);
		map_circles[questionId].push(
			L.circle(latlng, parseInt(
				$('#__internal_map_radius_id_'+questionId).val()
			))
		);
		map_circles[questionId][map_circles[questionId].length - 1].addTo(maps[questionId]);
	});
};

let mcqAddNewPotentialAnswer = function(){
	let questionId = $(this).data('question');
	let $body = $('#__internal_mcq_chooser_id_' + questionId);
	console.log($body);
	$body.prepend(
		$('<tr/>').append(
			$('<td/>').append(
				$('<input/>',{'type':'checkbox', 'class':''})
			),
			$('<td/>').append(
				$('<input/>',{'type':'text', 'class':'form-control'})
			)
		)
	);
};

let getQuestionTypeSchema = function(questionId, question_data) {
	let qs = copy(question_data);
	qs['text'] = $('#' + questionId + '_content :input').val();

	switch (question_data.questionType) {
		case 'map_choose':
			let map_locations = map_circles[questionId];
			let schema_locations = [];
			for (let location in map_locations) {
				schema_locations.push({
					'lat': map_locations[location]._latlng.lat,
					'lng': map_locations[location]._latlng.lng,
					'radius': map_locations[location].options.radius,
				});
			}
			console.log(schema_locations);
			qs['correct_locations'] = schema_locations;
			break;
		case 'multiple_choice':
			let choices = {};
			let tr_list = $('#__internal_mcq_chooser_id_' + questionId).find('tr');
			console.log(tr_list);
			for (let i = 0; i < tr_list.length; i++) {
				let $tr = $(tr_list[i]);
				let $tri = $tr.find('input');
				if ($tri.length !== 2) continue;

				console.log($tri);
				choices[$($tr.find('input[type="text"]')).val()] = !!$($tr.find('input[type="checkbox"]')).is(":checked");
			}
			qs['mcq'] = choices;
			break;
		case 'range_slider':
			qs['specified_range'] = {};
			qs['specified_range']['min'] = parseInt($('#__internal_range_min_id_' + questionId).val()) || 0;
			qs['specified_range']['step'] = parseInt($('#__internal_range_step_id_' + questionId).val()) || 1;
			qs['specified_range']['max'] = parseInt($('#__internal_range_max_id_' + questionId).val()) || 10;
			qs['specified_range']['lower'] = parseInt($('#__internal_bound_min_id_' + questionId).val()) || 0;
			qs['specified_range']['upper'] = parseInt($('#__internal_bound_max_id_' + questionId).val()) || 0;
			break;
		default:
			console.warn('Unknown type for schema collection:' + question_data.questionType);
			break;
	}

	return qs;
};

let createQuiz = function (evt) {
	evt.preventDefault();

	quiz_schema['name'] = $('#createquiz_name').val();
	quiz_schema['desc'] = $('#createquiz_desc').val();
	quiz_schema['type'] = $('#createquiz_type').val();

	let question_schema = {};
	for (let questionId in questions) {
		let question_data = questions[questionId];
		if (question_data['type'] === null) {
			continue;
		}
		console.log(question_data);
		question_schema[questionId] = getQuestionTypeSchema(questionId, question_data)
	}

	quiz_schema['questions'] = btoa(JSON.stringify(question_schema));
	console.log(quiz_schema);
	$('#save_submit').text('Saving...');

	$.ajax({
		url: '/l/api/create-quiz',
		type: 'POST',
		data: quiz_schema,
		dataType: 'json',
		success: function (resp) {
			if (!resp || resp.error === true) {
				_lancometer.apiErr(resp, 'Failed to load user information!');
				return;
			}
			$('#save_submit').text('Complete! Please wait...');

			if (resp.quiz_uuid) {
				window.location.href = '/l/manage-quiz';
			}
		},
		error: function (e) {
			_lancometer.apiErr(e, 'Failed to load user information!');
			$('#save_submit').text('Error!');
		}
	})
};

let getQuestionCount = function () {
	return $('#questions .question').length;
};

let generateMcqChooser = function (questionId) {
	return $('<table/>', {
		'class': 'mcq_answers table table-dark'
	}).append(
		$('<thead/>').append(
			$('<tr/>').append(
				$('<td/>').text('Is correct answer?'),
				$('<td/>').text('Answer text')
			)
		),
		$('<tbody/>',{'id':'__internal_mcq_chooser_id_' + questionId}).append(
			$('<tr/>').append(
				$('<td/>',{'colspan':'2'}).append(
					$('<button/>', {
						'class':'btn btn-light btn-block',
						'type':'button',
						'data-question': questionId
					}).text('Add new choice').on('click enter', mcqAddNewPotentialAnswer)
				)
			)
		)
	);
};

let generateMapChooser = function (questionId) {
	return $('<div/>').append(
		$('<div/>', {
			'class': 'form-group mt-1'
		}).append(
			$('<label/>').text('Radius (Meters)'),
			$('<input/>',{'type':'number', 'id':'__internal_map_radius_id_'+questionId, 'value':50, 'name':'circle_radius', 'class':'form-control'})
		),
		$('<div/>', {
			'class': 'form-group'
		}).append(
			$('<label/>').text('Map location (Select with left-click)'),
			$('<div/>', {
				'class': 'map_chooser',
				'id': '__internal_map_chooser_id_' + questionId,
				'data-question':questionId
			})
		)
	);
};

let generateRangeSlider = function (questionId) {
	return $('<div/>',{'class':'mt-2'}).append(
		$('<span/>',{'class':'h5 font-weight-light'}).text('Specify the range that the slider will display:'),
		$('<div/>',{'class':'row'}).append(
			$('<div/>',{'class':'col'}).append(
				$('<label/>').text('Minimum Value'),
				$('<input/>',{'type':'number', 'name':'slider_min', 'id':'__internal_range_min_id_'+questionId, 'class':'form-control', 'value':0})
			),
			$('<div/>',{'class':'col'}).append(
				$('<label/>').text('Step'),
				$('<input/>',{'type':'number', 'name':'slider_step', 'id':'__internal_range_step_id_'+questionId, 'class':'form-control', 'value':1})
			),
			$('<div/>',{'class':'col'}).append(
				$('<label/>').text('Maximum Value'),
				$('<input/>',{'type':'number', 'name':'slider_max', 'id':'__internal_range_max_id_'+questionId, 'class':'form-control', 'value':100})
			)
		),
		$('<span/>',{'class':'h5 font-weight-light'}).text('Specify the range that the correct answer lies in:'),
		$('<div/>',{'class':'row'}).append(
			$('<div/>',{'class':'col'}).append(
				$('<label/>').text('Lower Bound'),
				$('<input/>',{'type':'number', 'name':'bound_min', 'id':'__internal_bound_min_id_'+questionId, 'class':'form-control', 'value':5})
			),
			$('<div/>',{'class':'col'}).append(
				$('<label/>').text('Upper Bound'),
				$('<input/>',{'type':'number', 'name':'bound_max', 'id':'__internal_bound_max_id_'+questionId, 'class':'form-control', 'value':7})
			)
		)
	);
};

let getHTMLForQuestionType = function (questionId, type) {
	switch (type) {
		case 'map_choose':
			return generateMapChooser(questionId);
		case 'multiple_choice':
			return generateMcqChooser(questionId);
		case 'keywords':
		case 'answer_ranking':
		case 'organisation':
			break;
		case 'range_slider':
			return generateRangeSlider(questionId);
		default:
			alert('Question type not supported');
			return '';
	}
};

let runSetupForQuestionType = function (questionId, type) {
	switch(type) {
		case 'map_choose':
			setupLeafletMap(questionId);
			break;
		default:
			console.log('Question of type ' + type + ' requires no setup');
			break;
	}
};

let updateQuestionType = function (evt) {
	let questionId = $(this).data('question');
	let type = $(this).val();
	if (type === 'null') type = null;

	console.log('Changed question type to: ' + type + ' for ' + questionId);
	questions[questionId]['questionType'] = type;

	let $selector = $('#' + questionId + '_content');
	$selector.empty()

	if (type === null) return;
	$selector.append(
		$('<div/>',{'class':'row'}).append(
			$('<div/>',{'class':'col'}).append(
				$('<p/>',{'class':'lead'}).text(instructions[type]),
				$('<label/>').text('Question Text'),
				$('<input/>',{
					'type':'text',
					'placeholder':'E.g. What is a proton?',
					'required':'required',
					'class':'question_text form-control'
				})
			)
		),
		getHTMLForQuestionType(questionId, type)
	);

	runSetupForQuestionType(questionId, type)
};

let lastQuestionInt = 0;

let addNewQuestion = function (evt) {
	evt.preventDefault();

	document.getElementById('save_submit').disabled = false;

	if (getQuestionCount() === 0) {
		$('#questions').empty();
	}

	let questionId = _lancometer.genRandomId(16);

	questions[questionId] = {'questionType': null}

	$('#questions').append(
		$('<div/>', {
			'class': 'question m-3 text-light',
			'id': questionId
		}).append(
			$('<h4/>', { 'class': 'h5' }).append(
				$('<span/>',{'class':'pr-2'}).text(' Question #' + ++lastQuestionInt)
			).append(
				$('<button/>',{'class':'btn btn-sm btn-outline-danger'}).text('Delete')
			),
			$('<select/>', {
				'data-question': questionId,
				'class': 'form-control question_type'
			}).append(
				$('<option/>', { 'value': 'null', 'selected': true }).text('Please select a question type'),
				$('<option/>', { 'value': 'multiple_choice' }).text('Multiple Choice'),
				$('<option/>', { 'value': 'map_choose' }).text('Map Location'),
				//$('<option/>', { 'value': 'keywords' }).text('Keyword Selection'),
				$('<option/>', { 'value': 'answer_ranking' }).text('Answer Ranking'),
				//$('<option/>', { 'value': 'organisation' }).text('Organisation'),
				$('<option/>', { 'value': 'range_slider' }).text('Range Slider')
			).on('change', updateQuestionType),
			$('<div/>', {
				'id': questionId + '_content',
				'data-question': questionId,
				'class': 'm-1 question_custom_content'
			}).text('Once you select a question type, you can proceed to enter content.')
		)
	);
};

$('#create_quiz_form').on('submit', createQuiz);
$('#add_question').on('click enter', addNewQuestion);
