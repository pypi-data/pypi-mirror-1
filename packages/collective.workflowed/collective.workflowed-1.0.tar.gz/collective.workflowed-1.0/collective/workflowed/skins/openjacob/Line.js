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
function Line()
{
  /** @private **/
  this.lineColor = new Color(0,0,0);
  /** @private **/
  this.stroke=1;
  /** @private **/
  this.canvas=null;
  /** @private **/
  this.workflow=null;
  /** @private **/
  this.html=null;
  /** @private **/
  this.graphics = null;
  /** @private **/
  this.id = this.generateUId();
  /** @private **/
  this.startX = 30;
  /** @private **/
  this.startY = 30;
  /** @private **/
  this.endX   = 100;
  /** @private **/
  this.endY   = 100;
  // Hier werden Object registriert welche informiert werden wollen wenn sich dieses
  // Object bewegt hat.
  //
  this.moveListener = new Object();
}

Line.prototype = new Object;
/** @private **/
Line.prototype.type="Line";

/**
 * @private
 **/
Line.prototype.dispose=function()
{
//  this.id = null; required for deregistration
//  this.html=null;
  this.canvas = null;
  this.workflow=null;
  if(this.graphics != null)
    this.graphics.clear();
  this.graphics =null;
}

/**
 * @private
 **/
Line.prototype.createHTMLElement=function()
{
    var item = document.createElement('div');
    item.id        = this.id;
    item.style.position="absolute";
    item.style.left   = "0px";
    item.style.top    = "0px";
    item.style.height = "0px";
    item.style.width  = "0px";
    item.style.zIndex = "20";
  
    return item;
}

/**
 * @private
 **/
Line.prototype.getHTMLElement=function()
{
  if(this.html==null)
  {
    this.html = this.createHTMLElement();
  }
  return this.html;
}

/**
 * Flag for a compartment figure. A compartment is an container for other figure objects.
 * Per default the generic figure can't handle children. 
 * Only to be compatible to class "Figure"
 * @see: CompartmentFigure for the deefault implementation.
 *
 **/
Line.prototype.isCompartment = function()
{
   return false;
}


/**
 * only to be compatible to class "Figure"
 **/
Line.prototype.isResizeable=function()
{
  return false;
}

/**
 * @private
 **/
Line.prototype.setCanvas = function(canvas /*:Canvas*/)
{
  this.canvas = canvas;
  if(this.graphics!=null)
    this.graphics.clear();
  this.graphics = null;
}

/**
 * @private
 **/
Line.prototype.setWorkflow= function(workflow /*:Workflow*/)
{
  this.workflow = workflow;
  if(this.graphics!=null)
    this.graphics.clear();
  this.graphics = null;
}

/**
 * @private
 **/
Line.prototype.paint=function()
{
  if(this.graphics ==null)
    this.graphics = new jsGraphics(this.id);
  else
    this.graphics.clear();

  this.graphics.setStroke(this.stroke);
  this.graphics.setColor(this.lineColor.getHTMLStyle());
  this.graphics.drawLine(this.startX, this.startY, this.endX, this.endY);
  this.graphics.paint();
}
/**
 * 
 **/
Line.prototype.attachMoveListener = function(figure /*:Figure*/) 
{
  this.moveListener[figure.id]=figure;
}

/**
 *
 **/
Line.prototype.detachMoveListener = function(figure /*:Figure*/) 
{
  this.moveListener[figure.id]=null;
}

/**
 *
 **/
Line.prototype.fireMoveEvent=function()
{
  for(key in this.moveListener)
  {
    var target = this.moveListener[key];
    if(target!=null)
      target.onOtherFigureMoved(this);
  }
}

/**
 *
 **/
Line.prototype.onOtherFigureMoved=function(figure /*:Figure*/)
{
}

/**
 *
 **/
Line.prototype.setLineWidth=function(w /*:int*/)
{
  this.stroke=w;
  // Falls das element jemals schon mal gezeichnet worden ist, dann
  // muss jetzt ein repaint erfolgen
  if(this.graphics!=null)
    this.paint();
}


/**
 *
 **/
Line.prototype.setColor= function(color /*:Color*/)
{
  this.lineColor = color;
  // Falls das element jemals schon mal gezeichnet worden ist, dann
  // muss jetzt ein repaint erfolgen
  if(this.graphics!=null)
    this.paint();
}

/**
 * type Color
 **/
Line.prototype.getColor= function()
{
  return this.lineColor;
}

/**
 *
 **/
Line.prototype.setStartPoint= function(x /*:int*/, y /*:int*/)
{
  this.startX = x;
  this.startY = y;
  // Falls das element jemals schon mal gezeichnet worden ist, dann
  // muss jetzt ein repaint erfolgen
  if(this.graphics!=null)
    this.paint();
}

/**
 *
 **/
Line.prototype.setEndPoint= function(x /*:int*/, y /*:int*/)
{
  this.endX = x;
  this.endY = y;
  // Falls das element jemals schon mal gezeichnet worden ist, dann
  // muss jetzt ein repaint erfolgen
  if(this.graphics!=null)
    this.paint();
}

/**
 *
 **/
Line.prototype.getStartX= function()
{
  return this.startX;
}

/**
 *
 **/
Line.prototype.getStartY= function()
{
  return this.startY;
}

/**
 *
 **/
Line.prototype.getEndX= function()
{
  return this.endX;
}

/**
 *
 **/
Line.prototype.getEndY= function()
{
  return this.endY;
}

/**
 * @private
 **/
Line.prototype.generateUId=function() 
{
  var chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz";
  var string_length = 10;
  var maxTry = 10;
    nbTry = 0
    while (nbTry < 1000) 
    {
        var id = '';
        // generate string
        for (var i=0; i<string_length; i++) {
            var rnum = Math.floor(Math.random() * chars.length);
            id += chars.substring(rnum,rnum+1);
        }
        // check if there
        elem = document.getElementById(id);
        if (!elem) {
           return id
       }
       nbTry += 1
    }
    return null
}

Line.prototype.containsPoint= function(PX /*:int*/, PY/*:int*/)
{
  var X1 = this.startX;
  var Y1 = this.startY;
  var X2 = this.endX;
  var Y2 = this.endY;
  // Adjust vectors relative to X1,Y1
  // X2,Y2 becomes relative vector from X1,Y1 to end of segment
  X2 -= X1;
  Y2 -= Y1;
  // PX,PY becomes relative vector from X1,Y1 to test point
  PX -= X1;
  PY -= Y1;
  var dotprod = PX * X2 + PY * Y2;
  var projlenSq;
  if (dotprod <= 0.0) {
      // PX,PY is on the side of X1,Y1 away from X2,Y2
      // distance to segment is length of PX,PY vector
      // "length of its (clipped) projection" is now 0.0
      projlenSq = 0.0;
  } else {
      // switch to backwards vectors relative to X2,Y2
      // X2,Y2 are already the negative of X1,Y1=>X2,Y2
      // to get PX,PY to be the negative of PX,PY=>X2,Y2
      // the dot product of two negated vectors is the same
      // as the dot product of the two normal vectors
      PX = X2 - PX;
      PY = Y2 - PY;
      dotprod = PX * X2 + PY * Y2;
      if (dotprod <= 0.0) {
          // PX,PY is on the side of X2,Y2 away from X1,Y1
          // distance to segment is length of (backwards) PX,PY vector
          // "length of its (clipped) projection" is now 0.0
          projlenSq = 0.0;
      } else {
          // PX,PY is between X1,Y1 and X2,Y2
          // dotprod is the length of the PX,PY vector
          // projected on the X2,Y2=>X1,Y1 vector times the
          // length of the X2,Y2=>X1,Y1 vector
          projlenSq = dotprod * dotprod / (X2 * X2 + Y2 * Y2);
      }
  }
    // Distance to line is now the length of the relative point
    // vector minus the length of its projection onto the line
    // (which is zero if the projection falls outside the range
    //  of the line segment).
    var lenSq = PX * PX + PY * PY - projlenSq;
    if (lenSq < 0) {
        lenSq = 0;
    }
    return Math.sqrt(lenSq)<10;
}
