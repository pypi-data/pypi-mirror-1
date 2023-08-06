function galleryMove(side, elementnr)
{
	var element = jq('#stream' + elementnr);
	var button_left = jq('#gallery-move-left' + elementnr);
	var button_right = jq('#gallery-move-right' + elementnr);
	button_left.css({'display': 'block'});
	button_right.css({'display': 'block'});		

	var currentValue = element.css("left");
	var valueInt = parseInt(currentValue);
	var newValue;
	
	var images = element.find("img");
	var image;
	var elementWidth = 0;	
	
	for (var i=0; i<images.length; i++)
	{
		elementWidth += jq(images[i]).width()+27;
	}

	elementWidth -= 986;

	switch(side)
	{
		case 'left':
			newValue = valueInt + 800;
			break;
		case 'right':
			newValue = valueInt - 800;
			break;
	}

	if(newValue >= 0)
	{ 
		element.animate({'left': 0}, 200);
		button_left.css({'display': 'none'});
	}
	else if (newValue <= -elementWidth)
	{
		element.animate({'left': -elementWidth}, 200);
		button_right.css({'display': 'none'});
	}
	else
	{
		element.animate({'left': newValue}, 200); 
	}
};
