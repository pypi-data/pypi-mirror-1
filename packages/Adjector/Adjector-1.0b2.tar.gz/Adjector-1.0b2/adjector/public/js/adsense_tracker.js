/**
 *------------------------------------------------------------------------------
 * Copyright 2009-2010 David Isaacson, Stou Sandalski, Information Capsid
 * Copyright 2003-2008 OpenX Limited
 *
 * This file is part of the program Adjector.
 *
 * Adjector is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) version 3 of the License.
 *
 * Adjector is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Adjector. If not, see <http://www.gnu.org/licenses/>.
 *-----------------------------------------------------------------------------
 * 
 * From OpenX's ag-uncompressed.js (version 2.6.4)
 */
var adjector_adSenseDeliveryDone;
var adjector_adSensePx;
var adjector_adSensePy;

function adjector_adSenseClick(path)
{
    // Add cache buster here to ensure multiple clicks are recorded
	var cb = new String (Math.random());
    cb = cb.substring(2,11);

	var i = new Image();
	i.src = path + cb;
}

function adjector_adSenseLog(obj)
{
	if (typeof obj.parentNode != 'undefined')
	{
        parent = obj.parentNode;
        while(parent.tagName == 'INS'){ // escape from google's <ins> nodes
            parent = parent.parentNode
        }
        
		var t = parent.innerHTML;

        var params = t.match(/\/\*\s*adjector_click_track=([^ ]+)\s*\*\//)
		if (params)
		{
			adjector_adSenseClick(params[1]);
		}
	}
}

function adjector_adSenseGetMouse(e)
{
	// Adapted from http://www.howtocreate.co.uk/tutorials/javascript/eventinfo
	if (typeof e.pageX  == 'number')
	{
		//most browsers
		adjector_adSensePx = e.pageX;
		adjector_adSensePy = e.pageY;
	}
	else if (typeof e.clientX  == 'number')
	{
		//Internet Explorer and older browsers
		//other browsers provide this, but follow the pageX/Y branch
		adjector_adSensePx = e.clientX;
		adjector_adSensePy = e.clientY;

		if (document.body && (document.body.scrollLeft || document.body.scrollTop))
		{
			//IE 4, 5 & 6 (in non-standards compliant mode)
			adjector_adSensePx += document.body.scrollLeft;
			adjector_adSensePy += document.body.scrollTop;
		}
		else if (document.documentElement && (document.documentElement.scrollLeft || document.documentElement.scrollTop ))
		{
			//IE 6 (in standards compliant mode)
			adjector_adSensePx += document.documentElement.scrollLeft;
			adjector_adSensePy += document.documentElement.scrollTop;
		}
	}
}

function adjector_adSenseFindX(obj)
{
	var x = 0;
	while (obj)
	{
		x += obj.offsetLeft;
		obj = obj.offsetParent;
	}
	return x;
}

function adjector_adSenseFindY(obj)
{
	var y = 0;
	while (obj)
	{
		y += obj.offsetTop;
		obj = obj.offsetParent;
	}

	return y;
}

function adjector_adSensePageExit(e)
{
	var ad = document.getElementsByTagName("iframe");

	if (typeof adjector_adSensePx == 'undefined')
		return;

	for (var i = 0; i < ad.length; i++)
	{
		var adLeft = adjector_adSenseFindX(ad[i]);
		var adTop = adjector_adSenseFindY(ad[i]);
		var adRight = parseInt(adLeft) + parseInt(ad[i].width) + 15;
		var adBottom = parseInt(adTop) + parseInt(ad[i].height) + 10;
		var inFrameX = (adjector_adSensePx > (adLeft - 10) && adjector_adSensePx < adRight);
		var inFrameY = (adjector_adSensePy > (adTop - 10) && adjector_adSensePy < adBottom);

		//alert(adjector_adSensePx + ',' + adjector_adSensePy + ' ' + adLeft + ':' + adRight + 'x' + adTop + ':' + adBottom);

		if (inFrameY && inFrameX)
		{
			if (ad[i].src.match(/googlesyndication\.com|ypn-js\.overture\.com|googleads\.g\.doubleclick\.net/))
				adjector_adSenseLog(ad[i]);
		}
	}
}

function adjector_adSenseInit()
{
	if (document.all && typeof window.opera == 'undefined')
	{
		//ie
		var el = document.getElementsByTagName("iframe");

		for (var i = 0; i < el.length; i++)
		{
			if (el[i].src.match(/googlesyndication\.com|ypn-js\.overture\.com|googleads\.g\.doubleclick\.net/))
			{
				el[i].onfocus = function()
				{
					adjector_adSenseLog(this);
				}
			}
		}
	}
	else if (typeof window.addEventListener != 'undefined')
	{
		// other browsers
		window.addEventListener('unload', adjector_adSensePageExit, false);
		window.addEventListener('mousemove', adjector_adSenseGetMouse, true);
	}
}

function adjector_adSenseDelivery()
{
	if (typeof adjector_adSenseDeliveryDone != 'undefined' && adjector_adSenseDeliveryDone)
		return;

	adjector_adSenseDeliveryDone = true;

	if(typeof window.addEventListener != 'undefined')
	{
		//.. gecko, safari, konqueror and standard
		window.addEventListener('load', adjector_adSenseInit, false);
	}
	else if(typeof document.addEventListener != 'undefined')
	{
		//.. opera 7
		document.addEventListener('load', adjector_adSenseInit, false);
	}
	else if(typeof window.attachEvent != 'undefined')
	{
		//.. win/ie
		window.attachEvent('onload', adjector_adSenseInit);
	}
	else
	{
		//.. mac/ie5 and anything else that gets this far

		//if there's an existing onload function
		if(typeof window.onload == 'function')
		{
			//store it
			var existing = onload;

			//add new onload handler
			window.onload = function()
			{
				//call existing onload function
				existing();

				//call adsense_init onload function
				adjector_adSenseInit();
			};
		}
		else
		{
			//setup onload function
			window.onload = adjector_adSenseInit;
		}
	}
}

adjector_adSenseDelivery();
