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
 * @class A Node is the base class for all figures which can have {@link Port}s. A {@link Port} is the 
 * anchor for a {@link Connection} line.<br><br><b>Hint:</b> A {@link Port} is a green dot which can be draged and droped over another port.<br>
 *
 * @version 0.5
 * @author Andreas Herz
 * @constructor
 */
function Node()
{
  /** @private **/
  this.bgColor = null;
  /** @private **/
  this.lineColor = new Color(0,0,0);
  /** @private **/
  this.lineStroke=1;
  Figure.call(this);
}

Node.prototype = new Figure;
/** @private **/
Node.prototype.type="Node";


/**
 * @private
 **/
Node.prototype.dispose=function()
{
  for(key in this.ports)
  {
    var port = this.ports[key];
    if(port!=null)
      port.dispose();
  }
  this.ports = null;
  Figure.prototype.dispose.call(this);
}

/**
 * @private
 **/
Node.prototype.createHTMLElement=function()
{
    var item = Figure.prototype.createHTMLElement.call(this);
    item.style.width="auto";
    item.style.height="auto";
    item.style.margin="1px";
    item.style.padding="1px";
    item.style.border= this.lineStroke+"px solid "+this.lineColor.getHTMLStyle();
    item.style.fontSize="1px";
    if(this.bgColor!=null)
      item.style.backgroundColor=this.bgColor.getHTMLStyle();
    return item;
}

/**
 * @private
 **/
Node.prototype.paint=function()
{
  Figure.prototype.paint.call(this);
  for(key in this.ports)
  {
    var port = this.ports[key];
    if(port !=null)
      port.paint();
  }
}

/**
 * Return the port with the corresponding name.
 * @see Port#getName
 * @see Port#setName
 *
 * @param {String} portName The name of the port to return.
 * @return Returns the port with the hands over name or null.
 * @type Port
 **/
Node.prototype.getPort= function(/*:String*/ portName)
{
  if(this.ports==null)
    return null;
  for(key in this.ports)
  {
    var port = this.ports[key];
    if(port!=null)
    {
      if(port.getName() == portName)
        return port;
    }
  }
}

/**
 *
 * @param {Port} port The new port to add.
 * @param {int}  x The x position.
 * @param {int}  y The y position.
 **/
Node.prototype.addPort= function(/*:Port*/ port, /*:int*/ x, /*:int*/ y)
{
  if(this.ports==null)
    this.ports = new Object();

  this.ports[port.id]=port;
  port.setOrigin(x,y);
  port.setPosition(x,y);
  port.setParent(this);
  this.html.appendChild(port.getHTMLElement());
  if(this.workflow!=null)
  {
    this.workflow.registerPort(port);
  }
}

/**
 * @param {Port} port The port to remove.
 *
 **/
Node.prototype.removePort= function(/*:Port*/ port)
{
  if(this.ports!=null)
    this.ports[port.id]=null;
  try
  {
    this.html.removeChild(port.getHTMLElement());
  }
  catch(exc)
  {
    // es kann sein, dass es noch nicht eingehängt wurde
  }
  if(this.workflow!=null)
    this.workflow.unregisterPort(port);
  port.dispose();
}

/**
 * @private
 **/
Node.prototype.setWorkflow= function(/*:Workflow*/ workflow)
{
  var oldWorkflow = this.workflow;
  Figure.prototype.setWorkflow.call(this,workflow);

  if(oldWorkflow!=null)
  {
    for(key in this.ports)
    {
      var port = this.ports[key];
      if(port!=null)
        oldWorkflow.unregisterPort(port);
    }
  }

  if(this.workflow!=null)
  {
    for(key in this.ports)
    {
      var port = this.ports[key];
      if(port !=null)
        this.workflow.registerPort(port);
    }
  }
}

/**
 * Set the background color of the node.
 *
 * @param Color color The new background color of this figure
 **/
Node.prototype.setBackgroundColor= function(/*:Color*/ color)
{
  this.bgColor = color;
  if(this.bgColor!=null)
    this.html.style.backgroundColor=this.bgColor.getHTMLStyle();
  else
    this.html.style.backgroundColor="transparent";
}

/**
 * @see Figure#setBorder
 * @deprecated
 **/
Node.prototype.setColor= function(/*:Color*/ color)
{
  this.lineColor = color;
  this.html.style.border= this.lineStroke+"px solid "+this.lineColor.getHTMLStyle();
}


/**
 * @deprecated
 **/
Node.prototype.setLineWidth=function(w)
{
  this.lineStroke=w;
  this.html.style.border= this.lineStroke+"px solid black";
}
