/*!
 *	jwPlayer Plugin for jQuery
 *	This plugin is to interface the new JWPlayer Javascript API
 *	via jQuery object. Since the jwplayer object already supports
 * 	chaining, this is a super simple plugin.
 *
 * 	See JWPlayer javascript API documentation here:
 *	http://www.longtailvideo.com/support/jw-player/jw-player-for-flash-v5/12540/javascript-api-reference
 *
 *	Requires JWPlayer v5.3+ & jQuery (probably any version?, tested 1.4.x)
 *
 *	Copyright (c) 2011 Kevin Peno
 *	Released under MIT license
 *	http://www.opensource.org/licenses/mit-license.php
 */
(function( $, jw ){

	// Used to assign an ID to elements without one.
	var instances = 0;

	$.fn.jwplayer = function( options )
	{
		if ( typeof options === 'object' )
		{
			// JW Doesn't allow creating on items without an ID.
			if( !this.attr("id") )
				this.attr( "id", "jquery-jwplayer-" + (++instances) );

			// Figure out auto dimensions.
			options.width = typeof( options.width ) !=="undefined" ? options.width + "px" : this.width();
			options.height = typeof( options.height ) !=="undefined" ? options.height + "px" : this.height();

			return jw( this[0] ).setup( options );
		}
		else
		{
			return jw( this );
		}
	};
})( jQuery, jwplayer );
