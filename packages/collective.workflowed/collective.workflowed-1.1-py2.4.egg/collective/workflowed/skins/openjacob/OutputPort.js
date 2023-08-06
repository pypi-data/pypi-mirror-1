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
function OutputPort(/*:Figure*/ uiRepresentation)
{
  Port.call(this, uiRepresentation);

  /** @private **/
  this.maxFanOut = -1; // the maximimum connections which goes out of this port (-1 == inifinite)
}

OutputPort.prototype = new Port;
/** @private **/
OutputPort.prototype.type="OutputPort";

/**
 *
 **/
OutputPort.prototype.onDrop = function(/*:Port*/ port)
{
  if(this.getMaxFanOut()<=this.getFanOut())
    return;

  if(port.type!= this.type)
    Port.prototype.onDrop.call(this,port);
}

OutputPort.prototype.onDragstart = function(/*:int*/ x, /*:int*/ y)
{
  if(this.maxFanOut==-1)
    return true;

  if(this.getMaxFanOut()<=this.getFanOut())
    return false;

  return true;
}

/**
 *
 **/
OutputPort.prototype.onDragEnter = function(/*:Port*/ port)
{
  if(this.getMaxFanOut()<=this.getFanOut())
    return;

  if(this.type != port.type)
    Port.prototype.onDragEnter.call(this, port);
}

OutputPort.prototype.setMaxFanOut = function(/*:int*/ count)
{
  this.maxFanOut = count;
}

OutputPort.prototype.getMaxFanOut = function()
{
  return this.maxFanOut;
}

/**
 * @type int
 **/
OutputPort.prototype.getFanOut = function()
{
  if(this.getParent().workflow==null)
    return 0;

  var count =0;
  var lines = this.getParent().workflow.getLines();
  for(key in lines)
  {
    var line = lines[key];
    if(line!=null && line.type=="Connection")
    {
      if(line.getSource()==this)
        count++;
      else if(line.getTarget()==this)
        count++;
    }
  }
  return count;
}