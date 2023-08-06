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

function ToolTransition(palette /*:PaletteWindow*/)
{
  ToolGeneric.call(this,palette);
  this.setTooltip("Workflow Transition");
  return this
}

ToolTransition.prototype = new ToolGeneric;
ToolTransition.prototype.type="ToolTransition";


ToolTransition.prototype.execute=function(x /*:int*/, y/*:int*/)
{
  transition_name=prompt("Transition Id");
  if(!transition_name) return;
  addTransitionComplete=function(tool,transition_name) { 
    var figure = new TransitionWindow(transition_name);
    figure.setDimension(140,40);
    outputPort = new OutputPort();
    outputPort.setDirection(-1); 
    outputPort.setMaxFanOut(1); 
    outputPort.setWorkflow(workflow);
    outputPort.setBackgroundColor(new Color(115,245,115));
    inputPort = new InputPort();
    inputPort.setDirection(-1);
    inputPort.setWorkflow(workflow);
    inputPort.setBackgroundColor(new Color(245,115,111));
    inputPort.setColor(null);
    figure.addPort(outputPort,0,25);
    figure.addPort(inputPort,0,40);
    tool.palette.workflow.addFigure(figure,x,y);
    ToolGeneric.prototype.execute.call(tool,x,y);
  }
  addTransitionFailed=function() { alert('Error. Unable to add transition.'); }
  addTransitionURL="portal_workflow/"+document.location.search.split('=')[1]+"/transitions/addTransition?id="+transition_name;
  addTransition=new Ajax(addTransitionURL,{method:'get',onFailure:addTransitionFailed,onComplete:addTransitionComplete(this,transition_name)});
  addTransition.request();
}
