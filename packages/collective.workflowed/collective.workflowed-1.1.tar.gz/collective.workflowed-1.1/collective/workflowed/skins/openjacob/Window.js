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
function Window(title /*:String*/)
{
  /** @private **/
  this.title =title;
  /** @private **/
  this.titlebar=null;

  Figure.call(this);
}
Window.prototype = new Figure;
/** @private **/
Window.prototype.type="Window";

/**
 * Return true if the origin of the Object is the window and not
 * the document. This is usefull if you want implement a window or a
 * dialog element. The element doesn't move if the user scroll the document.
 *
 * @returns Returns [true] if the origin of the object the window.
 * @type boolean
 **/
Window.prototype.hasFixedPosition=function()
{
  return true;
}

/**
 * @private
 **/
Window.prototype.createHTMLElement=function()
{
  var item = Figure.prototype.createHTMLElement.call(this);
  item.style.margin="0px";
  item.style.padding="0px";
  item.style.border= "1px solid black";
  item.style.backgroundImage="url(window_bg.png)";
  item.style.zIndex="5000";
  item.style.cursor=null;

//  item.style.position="fixed";
  this.titlebar = document.createElement("div");
  this.titlebar.style.position="absolute";
  this.titlebar.style.left   = "0px";
  this.titlebar.style.top    = "0px";
  this.titlebar.style.width = this.getWidth()+"px";
  this.titlebar.style.height = "15px";
  this.titlebar.style.margin = "0px";
  this.titlebar.style.padding= "0px";
  this.titlebar.style.font="normal 10px verdana";
  this.titlebar.style.backgroundColor="blue";
  this.titlebar.style.borderBottom="2px solid gray";
  this.titlebar.style.whiteSpace="nowrap";
  this.titlebar.style.textAlign="center";
  this.titlebar.style.backgroundImage="url(window_toolbar.png)";
  this.textNode = document.createTextNode(this.title);
  this.titlebar.appendChild(this.textNode);

  item.appendChild(this.titlebar);
  return item;
}

/** 
 * @private
 **/
Window.prototype.setDocumentDirty=function( /*:Figure*/ figure)
{
  // a window can't invalidate a document.
  // Reason: Movement of a Dialog or Window is not relay a document modification.
}


/**
 * Will be called if the object are move via drag and drop.
 * Don't override this method if you want avoid the drag and drob of your window.
 * Use the setCanDrag(false) method instead.<br>
 *
 * @param {int} x x position of the mouse in the window
 * @param {int} y y position of the mouse in the window
 * @returns Returns [true] if the window can be draged. False in the other case
 * @type boolean
 **/
Window.prototype.onDragstart = function(/*:int*/ x, /*:int*/ y)
{
  // Return only true if the user klicks into the tilebar.
  // (Titlebar is the DragDrop handle for a window)
  //
  if(x<parseInt(this.titlebar.style.width) && y<parseInt(this.titlebar.style.height))
    return true;

  // add additional checks for the bootm/right resize handle
  // TODO

  return false;
}

/**
 * @private
 * @type boolean
 **/
Window.prototype.isSelectable=function()
{
  return false;
}

/**
 * Switch on/off the drag drop behaviour of this object
 * @param {boolean} flag The flag which handles the drag drop behaviour of this window.
 *
 **/
Window.prototype.setCanDrag=function(/*:boolean*/flag)
{
  Figure.prototype.setCanDrag.call(this,flag);
  this.html.style.cursor=null;
  if(flag)
    this.titlebar.style.cursor="move";
  else
    this.titlebar.style.cursor=null;
}


/**
 * Will be called from the framework if the figure/window has been added to a Workflow 
 * instance.
 *
 * @private
 **/
Window.prototype.setWorkflow= function( /*:Workflow*/ workflow)
{
  var oldWorkflow = this.workflow;
  Figure.prototype.setWorkflow.call(this,workflow);
  if(oldWorkflow!=null)
    oldWorkflow.removeSelectionListener(this);
  if(this.workflow!=null)
    this.workflow.addSelectionListener(this);
}

/**
 * Set the new dimension of the window.
 *
 * @param {int} w new width of the window. 
 * @param {int} h new height of the window. 
 **/
Window.prototype.setDimension=function(/*:int*/ w, /*:int*/ h)
{
  Figure.prototype.setDimension.call(this,w,h);
  if(this.titlebar!=null)
  {
    this.titlebar.style.width=this.getWidth()+"px";
  }
}

/**
 * Set the new title / header of this dialog.
 *
 * @param {String} title The new title of the window
 **/
Window.prototype.setTitle= function(/*:String*/ title)
{
  this.title = title;
}

/**
 * @type int
 **/
Window.prototype.getMinWidth=function()
{
  return 50;
}

/**
 * @type int
 **/
Window.prototype.getMinHeight=function()
{
  return 50;
}

/**
 *
 **/
Window.prototype.isResizeable=function()
{
  return false;
}

/**
 *
 **/
Window.prototype.isDeleteable=function()
{
  return false;
}

/**
 * Avoid the alpha blending during the drag and drop of an window. This will only cost 
 * performance and I think this is importand.
 * @private
 **/
Window.prototype.setAlpha=function(percent /*:int 0-1*/)
{
  // sieht nicht gut aus bei einem Fenster und kostet nur Resourcen
}

/**
 * Set the background color of the window.
 * @param {Color} color The new background color of the object.
 *
 **/
Window.prototype.setBackgroundColor= function(/*:Color*/ color)
{
  this.bgColor = color;
  if(this.bgColor!=null)
    this.html.style.backgroundColor=this.bgColor.getHTMLStyle();
  else
    this.html.style.backgroundColor="transparent";
}

/**
  * @param {Color} color The new border color of the window.
  *
 **/
Window.prototype.setColor= function(/*:Color*/ color)
{
  this.lineColor = color;
  item.style.border= this.lineStroke+"px solid "+this.lineColor.getHTMLStyle();
}


/**
 * mmmh, make this sense? 
 * Line width has beend mapped to the border width. 
 * TODO: Implement a propper setBorder() method for the window.
 *
 * @param {int} w The new border width of the window.
 **/
Window.prototype.setLineWidth=function(/*:int*/ w)
{
  this.lineStroke=w;
  this.html.style.border= this.lineStroke+"px solid black";
}

/**
 * Call back method of the framework if the selected object has been changed.
 *
 * @param {Figure} figure the object which has been selected.
 **/
Window.prototype.onSelectionChanged=function(/*:Figure*/ figure)
{
}

