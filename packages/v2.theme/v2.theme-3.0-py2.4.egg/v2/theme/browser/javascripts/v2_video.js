jq(document).ready( function()
{
	var items = jq(".pageWrapper .autoFlowPlayer img");
	var players = items.parent();
	
	players.each( function()
	{
		$f(this).getClip(0).update({autoPlay: true});
	});
});

v2_video = {};

v2_video.configure = function (element, hasLeadImage)
{	
	jq(element).attr("onclick", "");

	var player = $f(element);
	
	if(hasLeadImage && player )
	{
		player.getClip(0).update({autoPlay: true});
	}
	else
	{
		return true;
	}
};
