/* This notice must be untouched at all times.

Open-jACOB Draw2D
The latest version is available at
http://www.openjacob.org

Copyright (c) 2006 Andreas Herz. All rights reserved.
Created 5. 11. 2006 by Andreas Herz (Web: http://www.freegroup.de )

LICENSE: LGPL

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License (LGPL) as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA,
or see http://www.gnu.org/copyleft/lesser.html
*/
function ResizeImage()
{
  Figure.call(this);
  this.setDimension(100,100);
}

ResizeImage.prototype = new Figure;
ResizeImage.prototype.type="ResizeImage";

/**
 * Initial call of the framework. This is the right placce to create your HTML elements
 *
 * @private
 **/
ResizeImage.prototype.createHTMLElement=function()
{
    var item = Figure.prototype.createHTMLElement.call(this);

    this.img = document.createElement("img");
    this.img.style.position="absolute";
    this.img.style.left   = "0px";
    this.img.style.top    = "0px";
    this.img.src="Image.gif";

    item.appendChild(this.img);

    // Add an div above the img. Required for a propper drag&drop handling.
    // If you remove this div, the image will crap the event and the internal drag&drop handling
    // is corrupt......bug?
    //
    this.d = document.createElement("div");
    this.d.style.position = "absolute";
    this.d.style.left     = "0px";
    this.d.style.top      = "0px";

    item.appendChild(this.d);

    return item;
}
/**
 * Adjust the image if the user resize them
 *
 **/
ResizeImage.prototype.setDimension=function(/*:int*/ w, /*:int*/ h )
{
  Figure.prototype.setDimension.call(this,w, h);

  if(this.d!=null)
  {
    this.d.style.width  = this.width+"px";
    this.d.style.height = this.height+"px";

    this.img.width= this.width;
    this.img.height=this.height;
  }
}