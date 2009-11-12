$(function() {
	$.datepicker.setDefaults($.datepicker.regional['sk'])
	$('.datepicker').datepicker();
	$('.timepicker').timepickr({'trigger':'focus',prefix:['ráno','poobede'],suffix:['ráno','poobede']});
});