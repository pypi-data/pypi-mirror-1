/* cornerstone.js
 * 
 * Depends on jquery.
 * 
 * author: Robert Niederreiter <rnix@squarewave.at>
 */
/* Ajax namespace.
 */
cornerstone.ajax = function() {}
/* An Ajax response.
 * 
 * @param state: success state as int.
 * @param payload: the payload to render if success.
 * @param error: the error message to display if an error occurs
 */
cornerstone.ajax.Response = function(state, payload, error) {
	this.state = state;
	this.payload = payload;
	this.error = error;
}
/* This function gets called by the request transmit callback function of the
 * Request object.
 * 
 * @param handler: the handler given to the transmit function of the request.
 * 
 * XXX: A custom cornerstone Event must be thrown after the handler has
 *      returned
 */
cornerstone.ajax.Response.prototype.delegate = function(request, handler) {
	if (this.state != 0) {
		alert(this.error);
		return;
	}
    handler(request, this);
    // XXX: throw Event
}
/* An Ajax Request.
 * 
 * @param url: the url to call
 * @param params: Object containing the request parameters.
 */
cornerstone.ajax.Request = function(url, params) {
	this.url = url;
	this.params = params;
}
/* Function to perform the request.
 * 
 * This function calls the url with params defined by this.url and this.params
 * and expects return data in the following format:
 * 
 * <span class="response">
 *   <span class="responsestate">
 *     0 <!-- 0 is success, != 0 is error -->
 *   </span>
 *   <span class="responseerror">
 *     The Text of the error message to display if something went wrong.
 *   </span>
 *   <span class="responsepayload">
 *     The Payload to render if request was successful.
 *   </span>
 * </span>
 * 
 * @param handler: function to be called after response has been received. This
 *                 function gets the request object passed as parameter
 */
cornerstone.ajax.Request.prototype.transmit = function(handler) {
	var request = this;
	jQuery.get(this.url, this.params, function(data) {
		var state = jQuery('span.responsestate', data).html();
		state = parseInt(state);
		var error = jQuery('span.responseerror', data).html();
		var payload = jQuery('span.responsepayload', data).html();
		var response = new cornerstone.ajax.Response(state, payload, error);
		response.delegate(request, handler);
	});
}