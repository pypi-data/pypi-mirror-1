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

/**
 * 
 * @version 0.5
 * @author Andreas Herz
 * @constructor
 */
function Button(palette /*:PaletteWindow*/)
{
  /** @private **/
  this.x   = 0;
  /** @private **/
  this.y   = 0;
  /** @private **/
  this.id  = this.generateUId();
  /** @private **/
  this.enabled=true;
  /** @private **/
  this.palette = palette;
  this.setDimension(10,10);
  /** @private **/
  this.html = this.createHTMLElement();
}

Button.prototype.type="Button";

/**
 * @private
 **/
Button.prototype.dispose=function()
{
  //this.id   = null; don't dispose the id! This is important for deregistration
  //this.html = null; don't dispose the id! This is important for deregistration
}


Button.prototype.getImageUrl=function()
{
  if(this.enabled)
    return this.type+".png";
  else
    return this.type+"_disabled.png";
}


/**
 * @private
 **/
Button.prototype.createHTMLElement=function()
{
    var item = document.createElement('div');
    item.id        = this.id;
    item.style.position="absolute";
    item.style.left   = this.x+"px";
    item.style.top    = this.y+"px";
    item.style.height = "24px";
    item.style.width  = "24px";
    item.style.margin = "0px";
    item.style.padding= "0px";

    if(this.getImageUrl()!=null)
      item.style.backgroundImage="url("+this.getImageUrl()+")";
    else
      item.style.backgroundImage="";

    var oThis = this;
    this.omousedown=function(event)
    {
       if(oThis.enabled)
       {
          oThis.setActive(true);
       }
       event.cancelBubble = true;
       event.returnValue = false;
    }
    this.omouseup=function(event)
    {
       if(oThis.enabled)
       {
          oThis.setActive(false);
          oThis.execute();
       }
       event.cancelBubble = true;
       event.returnValue = false;
    }

    if (item.addEventListener) 
    {
      item.addEventListener("mousedown", this.omousedown, false);
      item.addEventListener("mouseup", this.omouseup, false);
    }
    else if (item.attachEvent) 
    {
      item.attachEvent("onmousedown", this.omousedown);
      item.attachEvent("onmouseup", this.omouseup);
    }

    return item;
}

/**
 * @private
 **/
Button.prototype.getHTMLElement=function()
{
  if(this.html==null)
    this.html = this.createHTMLElement();
  return this.html;
}


/**
 *
 **/
Button.prototype.execute=function()
{
}

/**
 * @private
 **/
Button.prototype.setActive=function(flag /*:boolean*/)
{
  if(!this.enabled)
    return;
  if(flag==true)
    this.html.style.border="2px inset";
  else
    this.html.style.border="0px";
}

/**
 * @private
 **/
Button.prototype.setEnabled=function(flag /*:boolean*/)
{
  this.enabled=flag;
  if(this.getImageUrl()!=null)
    this.html.style.backgroundImage="url("+this.getImageUrl()+")";
  else
    this.html.style.backgroundImage="";
}

/**
 *
 **/
Button.prototype.setDimension=function( w /*:int*/, h /*:int*/)
{
  this.width = w;
  this.height= h;

  // Falls das Element noch nie gezeichnet wurde, dann braucht aus das HTML nicht 
  // aktualisiert werden
  //
  if(this.html==null)
    return;

  this.html.style.width  = this.width+"px";
  this.html.style.height = this.height+"px";
}

/**
 *
 **/
Button.prototype.setPosition=function(xPos /*int*/, yPos /*int*/)
{
  this.x = Math.max(0,xPos);
  this.y = Math.max(0,yPos);
  // Falls das Element noch nie gezeichnet wurde, dann braucht aus das HTML nicht 
  // aktualisiert werden
  //
  if(this.html==null)
    return;

  this.html.style.left = this.x+"px";
  this.html.style.top  = this.y+"px";
}

/**
 *
 **/
Button.prototype.getWidth=function()
{
  return this.width;
}

/**
 *
 **/
Button.prototype.getHeight=function()
{
  return this.height;
}

/**
 *
 **/
Button.prototype.getY=function()
{
    return this.y;
}

/**
 *
 **/
Button.prototype.getX=function()
{
    return this.x;
}

/**
 *
 **/
Button.prototype.getPosition=function()
{
  return new Point(this.x, this.y);
}


/**
 * @private
 * @returns String
 **/
Button.prototype.generateUId=function() 
{
  var chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz";
  var string_length = 10;
  var maxTry = 10;
  nbTry = 0
  while (nbTry < 1000) 
  {
      var id = '';
      // generate string
      for (var i=0; i<string_length; i++) 
      {
          var rnum = Math.floor(Math.random() * chars.length);
          id += chars.substring(rnum,rnum+1);
      }
      // check if there
      elem = document.getElementById(id);
      if (!elem)
          return id
      nbTry += 1
  }
  return null
}
