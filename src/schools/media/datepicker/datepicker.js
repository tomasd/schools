$(function() {
	$.datepicker.setDefaults($.datepicker.regional['sk'])
	enable_datepicker();
});

var enable_datepicker = function(){
	$('.datepicker').datepicker();
	$('.timepicker').timepickr({'trigger':'focus',prefix:['ráno','poobede'],suffix:['ráno','poobede']});
};
var disable_datepicker = function() {
	$('.datepicker').datepicker('destroy');
	$('.timepicker').timepickr('destroy');
};