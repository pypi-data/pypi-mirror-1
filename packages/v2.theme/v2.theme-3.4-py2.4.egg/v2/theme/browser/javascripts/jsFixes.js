JsFixes = {};

JsFixes.fixCaptions = function ()
{
	var leadimage = jq(".newsImageContainer a img");
	var width = leadimage.width();
	jq(".newsImageContainer p").css({'max-width' : width});
};

JsFixes.fixImageLinks = function ()
{
	var siteURL = "http://"+top.location.host.toString();
	//alert(siteURL);

	jq(".pageWrapper a img[src^='"+siteURL+"']").parent().each(function()
	{
		if(jq(this).attr('id') != 'parent-fieldname-leadImage' && jq(this).attr('id') != 'parent-fieldname-image')
		{
			jq(this).attr('href', jq(this).attr('href')+'/view');
		}
	});
};

JsFixes.fixSquareThumbnails = function ()
{
	jq(".album_image").each(function ()
	{
		var image = jq(this).find("img:first-child");
		var width = image.width(); //get image width
		var height = image.height(); //get image height
		
		image.css({'margin-top': '-'+height/2+'px', 'margin-left': '-'+width/2+'px', 'top' : '50%', 'left' : '50%', 'position':'relative','display':'block'});
	});
};

JsFixes.runFixes = function ()
{
	//Add new fixes to this list to activate them.
	JsFixes.fixCaptions();
	JsFixes.fixImageLinks();
};


JsFixes.runSpecialFixes = function ()
{
	//Add new fixes to this list to activate them and ONLY RUN WHEN THE FULL PAGE IS LOADED
	JsFixes.fixSquareThumbnails();
};

//run all the fixes when the DOM is completely loaded;
jq(window).load(function () {JsFixes.runSpecialFixes();});
jq(document).ready(function () {JsFixes.runFixes();}); 
