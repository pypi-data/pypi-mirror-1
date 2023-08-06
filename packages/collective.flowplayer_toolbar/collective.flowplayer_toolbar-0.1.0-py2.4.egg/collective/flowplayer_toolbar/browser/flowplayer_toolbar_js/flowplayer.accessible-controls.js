/**
 * Javascript code for adding accessible toolbar to flowplayer players in the page 
 */

jq(document).ready(function(event) {
	$f("*").each(function() {
		this.onLoad(function(event) {
			this.getPlugin("controls").hide();
			var p = jq(this.getParent());
			var p_width = p.width();
			var time_width = (p_width<400?99:129);
			var hulu_id = "hulu-"+ (jq(".hulu").length+1);
			p.after('<div id="'+hulu_id+'" style="width:'+p_width+'px" class="hulu">\n'
				+'<a class="play" href="javascript:;" role="button">Play</a>\n'
				+'<div class="track" style="width:'+(p_width-46-46-time_width)+'px">\n'
				+'    <div class="buffer"></div>\n'
				+'    <div class="progress"></div>\n'
				+'    <div class="playhead"></div>\n'
				+'</div>\n'
				+'<div class="time" style="width:'+time_width+'px"></div>\n'
				+'<a class="mute" href="javascript:;" role="button">Mute</a>\n'
				+'</div>\n');
			this.controls(hulu_id);
			// Now I'll fix all other positions of the new toolbar
			jq("#"+hulu_id+" a.mute").css('left', p_width-46);
			jq("#"+hulu_id+" div.time").css('left', p_width-46-time_width);
		});
	});
});

