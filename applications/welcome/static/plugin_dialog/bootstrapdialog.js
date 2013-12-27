/*
********* Easy bootstrap dialog boxes for web2py **************
*/

$(document).ready(function() {
	// need id to pass to web2py_component
	$('.modal-body').attr('id', 'modal-body')
	
	$('.close').text("X")
	$('#myModalLabel').text("Please fill in the form")

	$('#myModal').modal({backdrop:false, show: false});
	$('#myModal').css({position: 'fixed', top: '150', left: '50%'})

	$('#myModal').on('shown', function () {
		$(this).find(':text:enabled:input:first').focus();
	});

	// close dialog on submit. Alternative is to use response.js to close on accept.
    $('#myModal').find('.btn-primary').click(function() {
	   	$('#modal-body').find('form').submit();
		closedialog()
	})	
})

// call controller and place result in dialog box
function getdialog(url) {
	web2py_component(url, 'modal-body');
}
// called by response.js after form is available
function opendialog() {
    $('#modal-body form :submit').css('display', 'none')
	$('#myModal').modal('show');
}
function closedialog() {
	$('#myModal').modal('hide');
}
 
// called by response.js to refresh any components that may have changed
function refresh(component) {
	$("#" + component).get(0).reload()
}