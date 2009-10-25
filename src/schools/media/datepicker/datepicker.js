$(function() {
	$('.datepicker').datepicker($.datepicker.regional['sk']);
	$('.timepicker').timepickr({'trigger':'focus',prefix:['ráno','poobede'],suffix:['ráno','poobede']});
});