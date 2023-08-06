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
 * @class A Connection is the line between two {@link Port}s.
 *
 * @version 0.5
 * @author Andreas Herz
 * @constructor
 */
function Connection()
{
  Line.call(this);

  /** @private **/
  this.sourcePort = null;
  /** @private **/
  this.targetPort = null;

  this.setColor(new Color(0,0,115));
  this.setLineWidth(1);
}

Connection.prototype = new Line;
  /** @private **/
Connection.prototype.type="Connection";


/**
 * @private
 **/
Connection.prototype.dispose=function()
{
  Line.prototype.dispose.call(this);

  if(this.sourcePort!=null)
    this.sourcePort.detachMoveListener(this);
  if(this.targetPort!=null)
    this.targetPort.detachMoveListener(this);

  this.sourcePort = null;
  this.targetPort = null;
}

/**
 * @private
 **/
Connection.prototype.paint=function()
{
  if(this.graphics ==null)
    this.graphics = new jsGraphics(this.id);
  else
    this.graphics.clear();

  this.graphics.setStroke(this.stroke);
  this.graphics.setColor(this.lineColor.getHTMLStyle());

/*
  // Draw a "L"
  //  |
  //  |---
  //
  if(this.sourcePort.getDirection()==3)
  {
    this.graphics.drawLine(this.startX, this.startY, this.startX, this.endY);
    this.graphics.drawLine(this.startX, this.endY, this.endX, this.endY);
  }
  // Draw a "L"
  //  |
  //  |---
  //
  else if(this.targetPort.getDirection()==3)
  {
    this.graphics.drawLine(this.startX, this.startY, this.endX, this.startY);
    this.graphics.drawLine(this.endX, this.startY, this.endX, this.endY);
  }
  // Draw a "Z" source=>target
  // -------
  //       |
  //       |____________
  //
  else if(this.sourcePort.getDirection()==2 && this.targetPort.getDirection()==4)
  {
    var center = (this.startX + this.endX)/2;
    this.graphics.drawLine(this.startX, this.startY, center, this.startY);
    this.graphics.drawLine(center, this.startY, center, this.endY);
    this.graphics.drawLine(center, this.endY, this.endX, this.endY);
  }
  // Draw a "Z" target=> source
  // -------
  //       |
  //       |____________
  //
  else if(this.targetPort.getDirection()==2 && this.sourcePort.getDirection()==4)
  {
    var center = (this.startX + this.endX)/2;
    this.graphics.drawLine(this.startX, this.startY, center, this.startY);
    this.graphics.drawLine(center, this.startY, center, this.endY);
    this.graphics.drawLine(center, this.endY, this.endX, this.endY);
  }
  else
  {
    this.graphics.drawLine(this.startX, this.startY, this.endX, this.endY);
  }
  this.graphics.paint();
*/
  this.fullAutoStroke();
}

/*
 * @private
 *
 **/
Connection.prototype.startStroke=function()
{
 this.oldPoint=null;
}

/*
 * @private
 *
 **/
Connection.prototype.finishStroke=function()
{
  this.graphics.paint();
  this.oldPoint=null;
}

/*
 * @private
 *
 **/
Connection.prototype.addPoint=function(/*:Point*/p)
{
  if(this.oldPoint!=null)
    this.graphics.drawLine(this.oldPoint.x,this.oldPoint.y, p.x, p.y);
  this.oldPoint = new Object();
  this.oldPoint.x = p.x;
  this.oldPoint.y = p.y;
}

/*
 * @private
 *
 **/
Connection.prototype.fullAutoStroke=function()
{
    // fromPt is an x,y to start from.  
    // fromDir is an angle that the first link must 
    //
    //  up     -> 0
    //  right  -> 1
    //  down   -> 2
    //  left   -> 3

    var fromPt  = new Point(this.startX, this.startY);
    var fromDir = this.sourcePort.getDirection();

    var toPt    = new Point(this.endX, this.endY);;
    var toDir   = this.targetPort.getDirection();

    // draw a line between the two points.
    this.startStroke();
    this.addPoint(fromPt);     // point 1


    var xseg = 30;	   //** new for rect links
    var yseg = 100;

    var xsegFrom = xseg;
    var xsegTo   = xseg;
    var ysegTo = yseg;

    //note: no getminYoffset, makes more sense for sides ports with labels. 

    // draw the Initial offset in Initial direction
    var cx = 0;
    var cy = 0;

    if (fromDir == 0) cy = yseg;
    if (fromDir == 1) cx = xsegFrom;
    if (fromDir == 2) cy = - yseg;
    if (fromDir == 3) cx = - xsegFrom;
    
       // simple direct connection
	if (fromDir == -1 && toDir == -1) {
           // do nothing
        }
	// do the simple ones (e.g. out the right and into the left of a node positioned to the right.)
	else if (fromDir == 1 && toDir == 3 && fromPt.x < toPt.x) {
		// to right
		fromPt.x = fromPt.x + ((toPt.x - fromPt.x) / 2);	// half way to next port (may be less than yseg)
		this.addPoint(fromPt);       // point 2
	}
	else if (fromDir == 0 && toDir == 2 && fromPt.y < toPt.y) {
		// up
		fromPt.y = fromPt.y + ((toPt.y - fromPt.y) / 2);	// half way to next port (may be less than yseg)
		this.addPoint(fromPt);       // point 2
	}
	else if (fromDir == 3 && toDir == 1 && fromPt.x > toPt.x) {
		// to left
		fromPt.x = fromPt.x - ((fromPt.x - toPt.x) / 2);	// half way to next port (may be less than yseg)
		this.addPoint(fromPt);       // point 2
	}
	else if (fromDir == 2 && toDir == 0 && fromPt.y > toPt.y) {
		// down
		fromPt.y = fromPt.y - ((fromPt.y - toPt.y) / 2);	// half way to next port (may be less than yseg)
		this.addPoint(fromPt);       // point 2
	}
	else {
		// none of the simple cases DoCalculateed out... do the more complicated routing

		fromPt.x = fromPt.x+cx;
                fromPt.y = fromPt.y+cy;
		this.addPoint(fromPt);       // point 2

		// may soon need info about parent areas of these ports
		var rectFrom = new Object();
                rectFrom.top    = this.sourcePort.parent.getY();
                rectFrom.bottom = this.sourcePort.parent.getY()+this.sourcePort.parent.getHeight();
                rectFrom.left   = this.sourcePort.parent.getX();
                rectFrom.right  = this.sourcePort.parent.getX()+this.sourcePort.parent.getWidth();

		var rectTo = new Object();
                rectTo.top    = this.targetPort.parent.getY();
                rectTo.bottom = this.targetPort.parent.getY()+this.targetPort.parent.getHeight();
                rectTo.left   = this.targetPort.parent.getX();
                rectTo.right  = this.targetPort.parent.getX()+this.targetPort.parent.getWidth();

		switch (toDir)
		{
		case 0: // into to the top.
			if (fromPt.y < (toPt.y + ysegTo))  {

				var y = 0;
				// "to" node is above "from" node, must put an
				// extra kink in the link.  (i.e. 2 more points)

				
				// go up the side of the from node
				fromPt = new Point(fromPt.x, Math.min(rectFrom.top+10, toPt.y + ysegTo));
				this.addPoint(fromPt);         // point 

                                if (fromPt.x > rectTo.left && fromPt.x < rectTo.right){ 	 // if to node to left
					this.addPoint(new Point(rectTo.left-10, rectFrom.top+10));  // point 
					this.addPoint(new Point(rectTo.left-10, toPt.y + ysegTo));  // point 
				}
				else {
					this.addPoint(new Point(fromPt.x,toPt.y + ysegTo));  // point 
				}

			} else {
				if (fromPt.x > toPt.x) 
					fromPt = new Point(fromPt.x, toPt.y + ysegTo);
				else
					fromPt = new Point(toPt.x, fromPt.y); 
				this.addPoint(fromPt);         // point 
			}
			break;
		case 1: // to the right
			if (fromPt.x < (toPt.x + xsegTo))  {

				var y = 0;
				// "to" node is to right of "from" node, must put an
				// extra kink in the link.  (i.e. 2 more points)

				if (fromPt.y < toPt.y) 				{
					// from pt below to point, route above From node
					if (rectFrom.top < rectTo.bottom) {
						// route half way  between top and bottom
						y = rectTo.bottom + ((rectFrom.top - rectTo.bottom) / 2);
					}
					else {
						// route over tops of both
						y = Math.max(rectFrom.top, rectTo.top) + 10;
					}
            
				}
				else{
					// from pt above to point, route below From node
					if (rectFrom.bottom > rectTo.top) {
						// route half way  between top and bottom
						y = rectFrom.bottom + ((rectTo.top - rectFrom.bottom) / 2);
					}
					else {
						// route below bottoms of both
						y = Math.min(rectFrom.bottom, rectTo.bottom) - 10;
					}
            
				}
                                var steigung = 8;
                                if(rectFrom.top>rectTo.top)
                                  steigung= -steigung;
				this.addPoint(new Point(fromPt.x, y-steigung));  // point 3

				fromPt = new Point(toPt.x+xsegTo, y+steigung);
				this.addPoint(fromPt);         // point 4
			}
			break;

		case 3:  // into the left side of the To node (typical dataflow left-to-right case)
			if (fromPt.x > (toPt.x - xsegTo))  {

				var y = 0;
				// "to" node is to left of "from" node, must put an
				// extra kink in the link.  (i.e. 2 more points)

				if (fromPt.y < toPt.y)
                                {
					// from pt below to point, route above From node
					if (rectFrom.top < rectTo.bottom) {
						// route half way  between top and bottom
						y = rectTo.bottom + ((rectFrom.top - rectTo.bottom) / 2);
					}
					else {
						// route over tops of both
						y = Math.max(rectFrom.top, rectTo.top) + 10;
					}
            
				}
				else{
					// from pt above to point, route below From node
					if (rectFrom.bottom > rectTo.top) {
						// route half way  between top and bottom
						y = rectFrom.bottom + ((rectTo.top - rectFrom.bottom) / 2);
					}
					else {
						// route below bottoms of both
						y = Math.min(rectFrom.bottom, rectTo.bottom) - 10;
					}
            
				}
				this.addPoint(new Point(fromPt.x, y));  // point 3

				fromPt = new Point(toPt.x-xsegTo, y);
				this.addPoint(fromPt);         // point 4

			}
			break;
		}
	}
   // calculate the point to make the link rectilinear                                   
   if (toDir == 1 || toDir == 3) {
    this.addPoint(new Point(fromPt.x, toPt.y));
   }
   else if (toDir == 0 || toDir == 2){
    this.addPoint(new Point(toPt.x, fromPt.y));
   }

  // now finish up
  this.addPoint(toPt);
  this.finishStroke();
}
/**
 *
 **/
Connection.prototype.setSource=function(/*:Port*/ port)
{
  if(this.sourcePort!=null)
    this.sourcePort.detachMoveListener(this);

  this.sourcePort = port;
  if(this.sourcePort==null)
    return;
  this.sourcePort.attachMoveListener(this);
  this.setStartPoint(port.getAbsoluteX(), port.getAbsoluteY());
}

/**
 * @type Port
 **/
Connection.prototype.getSource=function()
{
  return this.sourcePort;
}

/**
 *
 **/
Connection.prototype.setTarget=function(/*:Port*/ port)
{
  if(this.targetPort!=null)
    this.targetPort.detachMoveListener(this);

  this.targetPort = port;
  if(this.targetPort==null)
    return;
  this.targetPort.attachMoveListener(this);
  this.setEndPoint(port.getAbsoluteX(), port.getAbsoluteY());
}

/**
 * @type Port
 **/
Connection.prototype.getTarget=function()
{
  return this.targetPort;
}

/**
 * @see Figure#onOtherFigureMoved
 **/
Connection.prototype.onOtherFigureMoved=function(/*:Figure*/ figure)
{
  if(figure==this.sourcePort)
    this.setStartPoint(this.sourcePort.getAbsoluteX(), this.sourcePort.getAbsoluteY());
  else
    this.setEndPoint(this.targetPort.getAbsoluteX(), this.targetPort.getAbsoluteY());
}
