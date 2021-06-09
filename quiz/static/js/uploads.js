let uppy = Uppy.Core()

uppy.use(Uppy.Dashboard, {
	target: '#drag-drop-area',
	width: '100%',
	inline: true,
	replaceTargetContent: true,
	showProgressDetails: true,
	hidePauseResumeButton: true,
	theme: 'auto',
	proudlyDisplayPoweredByUppy: false
});

uppy.use(Uppy.XHRUpload, {
	formData: true,
	endpoint: '',
	method: 'POST',
	headers: {
		'X-CSRFToken': _lancometer._csrf
	},
	bundle: true,
	fieldName: 'file'
});

uppy.on('complete', (result) => {
	console.log('Upload complete! We’ve uploaded these files:', result.successful)
});
