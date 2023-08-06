/*
 * TODO: make this function a kss action
 */
function toggleComments(uid) {
	$('#' + uid + '_headline').toggleClass('commentsopen');
	$('#' + uid).toggleClass('hiddenComments');
}