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
function TransitionWindow(/*:String */ title)
{
  /** @private **/
  if(title)
     this.title = title;
  else
     this.title = "";
  /** @private **/
  this.titlebar=null;

  this.defaultBackgroundColor = new Color(130,130,250);
  this.highlightBackgroundColor = new Color(250,250,200);

  Node.call(this);
  this.setBackgroundColor(this.defaultBackgroundColor);
}

TransitionWindow.prototype = new Node;
TransitionWindow.prototype.type="TransitionWindow";



/**
 * @private
 **/
TransitionWindow.prototype.createHTMLElement=function()
{
  var item = Node.prototype.createHTMLElement.call(this);
  item.style.margin="0px";
  item.style.padding="0px";
  item.style.border= "1px solid black";
  item.style.cursor=null;

  this.titlebar = document.createElement("div");
  this.titlebar.style.position="absolute";
  this.titlebar.style.left   = "0px";
  this.titlebar.style.top    = "0px";
  this.titlebar.style.width = (this.getWidth()-5)+"px";
  this.titlebar.style.height = "15px";
  this.titlebar.style.margin = "0px";
  this.titlebar.style.padding= "0px";
  this.titlebar.style.font="normal 10px verdana";
  this.titlebar.style.backgroundColor="blue";
  this.titlebar.style.borderBottom="1px solid gray";
  this.titlebar.style.borderLeft="5px solid transparent";
  this.titlebar.style.whiteSpace="nowrap";
  this.titlebar.style.textAlign="left";
  this.titlebar.style.backgroundImage="url(window_toolbar.png)";
  this.textNode = document.createTextNode("TRANSITION");
  this.titlebar.appendChild(this.textNode);

  this.transitionid = document.createElement("div");
  this.transitionid.innerHTML = '<b>'+this.title+'</b>';
  this.transitionid.style.fontFamily="sans-serif";
  this.transitionid.style.fontSize="8pt";
  this.transitionid.style.position="absolute";
  this.transitionid.style.left   = "15px";
  this.transitionid.style.top    = "28px";

  item.appendChild(this.titlebar);
  item.appendChild(this.transitionid);
  return item;
}


/**
 * @param {int} w new width of the window. 
 * @param {int} h new height of the window. 
 **/
TransitionWindow.prototype.setDimension=function( w /*:int*/, h /*:int*/)
{
  CompartmentFigure.prototype.setDimension.call(this,w,h);
  if(this.titlebar!=null)
  {
    this.titlebar.style.width=(this.getWidth()-5)+"px";
  }
}

/**
 * @param {String} title The new title of the window
 **/
TransitionWindow.prototype.setTitle= function(title /*:String*/)
{
  this.title = title;
}

/**
 * @type int
 **/
TransitionWindow.prototype.getMinWidth=function()
{
  return 50;
}

/**
 * @type int
 **/
TransitionWindow.prototype.getMinHeight=function()
{
  return 50;
}


/**
 *
 **/
TransitionWindow.prototype.setBackgroundColor= function(/*:Color*/ color)
{
  this.bgColor = color;
  if(this.bgColor!=null)
    this.html.style.backgroundColor=this.bgColor.getHTMLStyle();
  else
    this.html.style.backgroundColor="transparent";
}

TransitionWindow.prototype.dispose=function()
{
  delTransitionComplete=function(transition_window) {
    Node.prototype.dispose.call(transition_window);
  }
  delTransitionFailed=function() { alert('Error. Unable to delete transition.'); }
  delTransitionURL="portal_workflow/"+document.location.search.split('=')[1]+"/transitions/deleteTransitions?ids:list="+this.title;
  delTransition=new Ajax(delTransitionURL,{method:'get',onFailure:delTransitionFailed,onComplete:delTransitionComplete(this)});
  delTransition.request();
}
