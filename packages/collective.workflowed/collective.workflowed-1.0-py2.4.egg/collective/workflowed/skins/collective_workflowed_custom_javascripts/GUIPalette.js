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

function GUIPalette()
{
  ToolPalette.call(this, "Tools");

  this.tool0 = new ToolSelection(this);
  this.tool1 = new ToolState(this);
  this.tool2 = new ToolTransition(this);
  //this.tool3 = new ToolWorklist(this);

  this.tool0.setPosition(20,30);
  this.tool1.setPosition(20,80);
  this.tool2.setPosition(20,130);
  //this.tool3.setPosition(20,180);


  this.addChild(this.tool0);
  this.addChild(this.tool1);
  this.addChild(this.tool2);
  //this.addChild(this.tool3);

  return this;
}
GUIPalette.prototype = new ToolPalette;
GUIPalette.prototype.type="GUIPalette";


GUIPalette.prototype.dispose=function()
{
  ToolPalette.prototype.dispose.call(this);
  this.tool0.dispose();
  this.tool1.dispose();
  this.tool2.dispose();
  //this.tool3.dispose();
}

GUIPalette.prototype.addChildren=function(item /*: HTMLElement*/)
{
}
