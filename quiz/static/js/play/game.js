let maps = {};
let map_circles = {};

let setupLeafletMap = function(questionId) {
	maps[questionId] = L.map('__internalgame_map_chooser_id_' + questionId, {
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
			L.circle(latlng, 10)
		);
		map_circles[questionId][map_circles[questionId].length - 1].addTo(maps[questionId]);
		_game.saving();
	});
};

let _game = {

	data:{},
	answer_data:{},

	loadData:function(){
		_api.request('game/load', {}, function(data) {
			_game.data = data.response;
			_game.makeGameHTML();
		},function (err){
			console.error(err);
			alert('Error')
		});
	},

	sendAnswer: function() {
		let answer_data = _game.answer_data;
		_api.request('game/answer', answer_data, function(data) {

		},function (err){
			console.error(err);
			alert('Error saving your answers')
		});
	},

	saving: function() {
		console.log(this);
		$("#saving_text").fadeIn(500).delay(100 * Math.random()).fadeOut(500);
		_game.sendAnswer();
	},

	init:function () {
		_game.loadData();
	},

	makeGameHTML: function (){
		console.log('We got game data!');
		console.log(_game.data);

		// Store the questions locally
		let qs = _game.data.questions;
		let qk = Object.keys(qs);
		let questionCount = qk.length;

		// Set title and description
		$('#quiz_name').text(_game.data.name);
		$('#quiz_desc').text(_game.data.desc || 'Quiz has no description.');

		$('#main_game').empty();

		// Loop all the questions
		for (let i = 0; i < questionCount; i++) {
			let questionId = qk[i];
			_game.addHTMLQuestionSeparator(i + 1, questionId);
			$('#main_game').append(
				_game.makeQuestionHTML(questionId, qs[questionId])
			);
		}
    },

	addHTMLQuestionSeparator: function(qInt, questionId) {
		$('#main_game').append(
			$('<p/>',{'class':'h3'}).text('Question #' + qInt),
			$('<div/>',{
				'id':'game_question_id_' + questionId,
				'data-question':questionId
			})
		);
	},

	makeQuestionHTML: function (questionId, qd) {
		console.log(qd);
		let type = qd.questionType;
		let doesQuestionTypeExist = !!_game.q[type];
		if (doesQuestionTypeExist) {
			return _game.q[type](questionId, qd);
		} else {
			return $('<div/>').text('Question type not found: ' + type);
		}
	},

	q: {
		map_choose: function(questionId, qd) {
			$('#game_question_id_' + questionId).empty().append(
				$('<p/>',{'class':'lead'}).text(qd.text),
				$('<div/>', {'class':'map_chooser', 'id':'__internalgame_map_chooser_id_' + questionId})
			);

			setupLeafletMap(questionId);

			return [];
		},

		multiple_choice: function(questionId, qd) {
			let $qcont = $('#game_question_id_' + questionId);
			$qcont.empty().append(
				$('<p/>',{'class':'lead'}).text(qd.text)
			);

			let keys = Object.keys(qd['mcq']);
			for (let i = 0; i < keys.length; i++) {
				$qcont.append(
					$('<div/>',{'class':'form-check'}).append(
						$('<input/>', {'type':'checkbox', 'class':'form-check-input', 'id':'__internalgame_mcq_id_' + questionId + '_' + i, 'data-question':questionId}).on('change', _game.saving),
						$('<label/>', {'class':'form-check-label', 'for':'__internalgame_mcq_id_' + questionId + '_' + i}).text(keys[i])
					)
				);
			}

			return [];
		},

		answer_ranking: function(questionId, qd) {

			return [];
		},

		range_slider: function(questionId, qd) {
			if (!qd['specified_range']){
				return [];
			}
			let defaultValue = qd['specified_range']['min'] + qd['specified_range']['max'] / 2;

			$('#game_question_id_' + questionId).empty().append(
				$('<label/>',{
					'class':'form-label lead',
					'for':'__internalgame_range_id_' + questionId
				}).text(qd.text),
				$('<input/>', {
					'type':'range',
					'class':'form-control-range',
					'id':'__internalgame_range_id_' + questionId,
					'min':qd['specified_range']['min'],
					'max': qd['specified_range']['max'],
					'step':qd['specified_range']['step'],
					'value': defaultValue,
					'data-question':questionId
				}).on('change', _game.saving)
			);
			return [];
		},

		organisation: function(questionId, qd) {

			return [];
		}
	}

};

_game.init();
