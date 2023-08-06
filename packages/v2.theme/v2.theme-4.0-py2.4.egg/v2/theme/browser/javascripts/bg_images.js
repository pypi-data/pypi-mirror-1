bkground = {};

bkground.img_number_max = 300;

bkground.getCookie = function(c_name)
{
	if (document.cookie.length>0)
	  {
	  c_start=document.cookie.indexOf(c_name + "=");
	  if (c_start!=-1)
	    {
	    c_start=c_start + c_name.length+1;
	    c_end=document.cookie.indexOf(";",c_start);
	    if (c_end==-1) c_end=document.cookie.length;
	    return unescape(document.cookie.substring(c_start,c_end));
	    }
	  }
	return "";
}

bkground.setCookie = function(c_name,value,expiredays)
{
	var exdate=new Date();
	exdate.setDate(exdate.getDate()+expiredays);
	document.cookie=c_name+ "=" +escape(value)+
	((expiredays==null) ? "" : ";expires="+exdate.toGMTString()+"; path=/");
}


bkground.gen_bkground = function()
{
	cookie_val=bkground.getCookie('bkground_img_number');
    bkground.direction = parseInt(bkground.getCookie('bkground_direction'));

    var bkground_img_number = parseInt(cookie_val)
    // sanatize cookie result values
    if (isNaN(bkground_img_number)){
        bkground_img_number = 10;
        bkground.direction = 10;
        bkground.setCookie('bkground_direction', bkground.direction,365);
    }
    
    //$('#counter_msg').html("Debug "+bkground_img_number+' '+bkground.direction);
    if (bkground_img_number >= bkground.img_number_max
	    || bkground_img_number <= 1) {
		if(bkground.direction > 0) {
           bkground.direction = -10;
           bkground.setCookie('bkground_direction', bkground.direction,365);
        } else {
           bkground.direction = 10;
           bkground.setCookie('bkground_direction', bkground.direction,365);
        }
	}
    
    
    bkground_img_number+=bkground.direction;

	bkground.setCookie('bkground_img_number', bkground_img_number,365);
	
	document.getElementById("portal-columns").style.backgroundImage = 'url(bg_image_'+bkground_img_number+'.jpg)'; 
}


window.addEventListener("load",bkground.gen_bkground,false);
//$(document).ready(function(){
//    bkground.gen_bkground();
//});
