JsFixes = {};

JsFixes.fixCaptions = function ()
{
	var leadimage = jq(".newsImageContainer a img");
	var width = leadimage.width();
	jq(".newsImageContainer p").css({'max-width' : width});
};

/*JsFixes.fixImageLinks = function ()
{
	jq(".image-inline img").each(function ()
	{
		if ()
		{	
		}
		else
		{
		}
	});
}*/

JsFixes.runFixes = function ()
{
	//Add new fixes to this list to activate them.
	JsFixes.fixCaptions();
};


//run all the fixes when page is completely loaded;
jq(document).ready(function () {JsFixes.runFixes();}); 
