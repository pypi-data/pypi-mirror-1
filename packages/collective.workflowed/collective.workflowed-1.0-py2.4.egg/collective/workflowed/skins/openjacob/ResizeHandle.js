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

/*
    1             2               3
      O-----------O-------------O
      |                         |
      |                         |
    8 O                         O 4
      |                         |
      |                         |
      O-----------O-------------O
    7             6               5

TYPE
*/

/**
 * 
 * @version 0.5
 * @author Andreas Herz
 * @constructor
 */
function ResizeHandle(/*:Workflow*/ workflow,  /*:int*/ type)
{
  /** @private **/
  this.type = type;
  Rectangle.call(this);
  this.setDimension(5,5);
  this.setBackgroundColor(new Color(0,255,0));
  this.setWorkflow(workflow);
}

ResizeHandle.prototype = new Rectangle;
/** @private **/
ResizeHandle.prototype.type="ResizeHandle";

/**
 * @private
 **/
ResizeHandle.prototype.dispose()
{
  Rectangle.prototype.dispose.call(this);
}

/**
 *
 **/
ResizeHandle.prototype.onDrag = function()
{
  var oldX = this.getX()
  var oldY = this.getY();
  Rectangle.prototype.onDrag.call(this);
  var diffX = oldX-this.getX();
  var diffY = oldY-this.getY();

  var objPosX = this.workflow.currentSelection.getX();
  var objPosY = this.workflow.currentSelection.getY();
  var objWidth= this.workflow.currentSelection.getWidth();
  var objHeight= this.workflow.currentSelection.getHeight();
  switch(this.type)
  {
    case 1:
      this.workflow.currentSelection.setPosition(objPosX-diffX, objPosY-diffY);
      this.workflow.currentSelection.setDimension(objWidth+diffX, objHeight+diffY);
      break;
    case 2:
      this.workflow.currentSelection.setPosition(objPosX, objPosY-diffY);
      this.workflow.currentSelection.setDimension(objWidth, objHeight+diffY);
      break;
    case 3:
      this.workflow.currentSelection.setPosition(objPosX, objPosY-diffY);
      this.workflow.currentSelection.setDimension(objWidth-diffX, objHeight+diffY);
      break;
    case 4:
      this.workflow.currentSelection.setPosition(objPosX, objPosY);
      this.workflow.currentSelection.setDimension(objWidth-diffX, objHeight);
      break;
    case 5:
      this.workflow.currentSelection.setPosition(objPosX, objPosY);
      this.workflow.currentSelection.setDimension(objWidth-diffX, objHeight-diffY);
      break;
    case 6:
      this.workflow.currentSelection.setPosition(objPosX, objPosY);
      this.workflow.currentSelection.setDimension(objWidth, objHeight-diffY);
      break;
    case 7:
      this.workflow.currentSelection.setPosition(objPosX-diffX, objPosY);
      this.workflow.currentSelection.setDimension(objWidth+diffX, objHeight-diffY);
      break;
    case 8:
      this.workflow.currentSelection.setPosition(objPosX-diffX, objPosY);
      this.workflow.currentSelection.setDimension(objWidth+diffX, objHeight);
      break;
  }
  this.workflow.moveResizeHandles(this.workflow.currentSelection);
}

ResizeHandle.prototype.setCanDrag=function(/*:boolean*/ flag)
{
  Rectangle.prototype.setCanDrag.call(this,flag);
  if(!flag)
  {
    this.html.style.cursor="";
    return;
  }

  switch(this.type)
  {
    case 1:
      this.html.style.cursor="nw-resize";
      break;
    case 2:
      this.html.style.cursor="n-resize";
      break;
    case 3:
      this.html.style.cursor="ne-resize";
      break;
    case 4:
      this.html.style.cursor="w-resize";
      break;
    case 5:
      this.html.style.cursor="nw-resize";
      break;
    case 6:
      this.html.style.cursor="n-resize";
      break;
    case 7:
      this.html.style.cursor="ne-resize";
      break;
    case 8:
      this.html.style.cursor="w-resize";
      break;
  }
}


/**
 *
 **/
ResizeHandle.prototype.onKeyDown=function( /*:int*/keyCode)
{
  // don't call the parent function. The parent functions delete this object
  // and a resize handle can't be deleted.
}
