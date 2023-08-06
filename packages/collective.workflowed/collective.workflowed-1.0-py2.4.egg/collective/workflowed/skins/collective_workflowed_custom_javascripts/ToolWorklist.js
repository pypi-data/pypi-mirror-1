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

function ToolWorklist(palette /*:PaletteWindow*/)
{
  ToolGeneric.call(this,palette);
  this.setTooltip("Worklist");
  return this;
}

ToolWorklist.prototype = new ToolGeneric;
ToolWorklist.prototype.type="ToolWorklist";


ToolWorklist.prototype.execute=function(x /*:int*/, y/*:int*/)
{
  state_name=prompt("State Id");
  if (!state_name) return;
  addStateComplete=function(tool,state_name) { 
    var figure = new StateWindow(state_name);
    figure.setDimension(160,40);
    outputPort = new OutputPort();
    outputPort.setDirection(-1);
    outputPort.setMaxFanOut(1000);
    outputPort.setWorkflow(workflow);
    outputPort.setBackgroundColor(new Color(245,115,115));
    inputPort = new InputPort();
    inputPort.setDirection(-1);
    inputPort.setWorkflow(workflow);
    inputPort.setBackgroundColor(new Color(115,245,115));
    inputPort.setColor(null);
    figure.addPort(outputPort,160,25);
    figure.addPort(inputPort,160,40);
    tool.palette.workflow.addFigure(figure,x,y);
    ToolGeneric.prototype.execute.call(tool,x,y);
  }
  addStateFailed=function() { alert('Error. Unable to add state.'); }
  addStateURL="portal_workflow/"+document.location.search.split('=')[1]+"/states/addState?id="+state_name;
  addState=new Ajax(addStateURL,{method:'get',onFailure:addStateFailed,onComplete:addStateComplete(this,state_name)});
  addState.request();
}
