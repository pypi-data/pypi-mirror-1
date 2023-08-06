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
 * @class A Port is the anchor for a {@link Connection}. A {@link Connection} must have a start and a end Port.
 * <br>
 * @version 0.5
 * @author Andreas Herz
 * @param {Figure} uiRepresentation The figure to paint this Port. This parameter is optional.
 * @constructor
 */
function Port(/*:Figure*/ uiRepresentation)
{
  // Die graphische Representation des Elementes
  //
  if(uiRepresentation==null)
    this.uiRepresentation = new Circle();
  else
    this.uiRepresentation = uiRepresentation;

  /** @private **/
  this.parent = null;
  /** @private **/
  this.originX=0; // the fix point of the point.
  /** @private **/
  this.originY=0;

  // prefered direction of the port
  //  -1 = direct
  //   0 = top
  //   1 = right
  //   2 = bottom
  //   3 = left
  /** @private **/
  this.direction = -1;

  Rectangle.call(this);
  this.setDimension(12,12);
  this.setBackgroundColor(new Color(100,180,100));
  this.setColor(new Color(90,150,90));
  Rectangle.prototype.setColor.call(this,null);
  /** @private **/
  this.dropable = new DropTarget(this.html);
  this.dropable.node = this;
  this.dropable.addEventListener("dragenter", function (oEvent)
  {
    oEvent.target.node.onDragEnter(oEvent.relatedTarget.node);
  });
  this.dropable.addEventListener("dragleave", function (oEvent)
  {
    oEvent.target.node.onDragLeave(oEvent.relatedTarget.node);
  });
  this.dropable.addEventListener("drop", function (oEvent)
  {
    oEvent.relatedTarget.node.onDrop(oEvent.target.node);
  });
}

Port.prototype = new Rectangle;
/** @private **/
Port.prototype.type="Port";

/**
 * @private
 **/
Port.prototype.dispose=function()
{
  // Remove all Connections which are bounded to this port
  // In this case this are alle movement listener
  for(key in this.moveListener)
  {
    var target = this.moveListener[key];
    if(target!=null)
    {
      this.parent.workflow.removeFigure(target);
      target.dispose();
    }
  }

  Figure.prototype.dispose.call(this);
  this.parent = null;
  this.dropable.node=null;
  this.dropable = null;
  this.uiRepresentation.dispose();
}



/**
 * @private
 **/
Port.prototype.createHTMLElement=function()
{
    var item = Rectangle.prototype.createHTMLElement.call(this);
    item.style.zIndex=4000;
    item.appendChild(this.uiRepresentation.html);
    return item;
}

/**
 * Set the representation of this port. The default representation of a port is a green circle.
 *
 * @param {Figure} figure The new UI representation of this port.
 **/
Port.prototype.setUiRepresentation=function(/*:Figure*/ figure)
{
  this.uiRepresentation.dispose();
  this.uiRepresentation = figure;
}

/**
 * Callback method for the mouse enter event. Usefull for mouse hover-effects.
 * @private
 **/
Port.prototype.onMouseEnter=function()
{
    this.setLineWidth(2);
}


/**
 * Callback method for the mouse leave event. Usefull for mouse hover-effects.
 * @private
 **/
Port.prototype.onMouseLeave=function()
{
    this.setLineWidth(0);
}


/**
 * Set the dimension of this port.
 *
 * @param {int} width The new width of the object
 * @param {int} heightThe new height of the object
 **/
Port.prototype.setDimension=function(/*:int*/ width, /*:int*/ height)
{
  Rectangle.prototype.setDimension.call(this, width, height);
  this.uiRepresentation.setDimension(width, height);
}

/**
 * Set the background color of the port
 * @param {Color} color The new background color of the port. 
 **/
Port.prototype.setBackgroundColor=function(/*:Color*/ color)
{
  // delegate to the UI representation
  this.uiRepresentation.setBackgroundColor(color);
}

Port.prototype.getBackgroundColor=function()
{
  // delegate to the UI representation
  return this.uiRepresentation.getBackgroundColor();
}

/**
 * Set the foreground color of the port
 * @param {Color} color The new foreground color of the port. 
 **/
Port.prototype.setColor=function(/*:Color*/ color)
{
  // delegate to the UI representation
  this.uiRepresentation.setColor(color);
}

Port.prototype.getColor=function()
{
  // delegate to the UI representation
  return this.uiRepresentation.getColor();
}

/**
 * Set the foreground color of the port
 * @param {Color} color The new foreground color of the port. 
 **/
Port.prototype.setLineWidth=function(/*:int*/ width)
{
  // delegate to the UI representation
  this.uiRepresentation.setLineWidth(width);
}

Port.prototype.getLineWidth=function()
{
  // delegate to the UI representation
  return this.uiRepresentation.getLineWidth();
}

/**
 * @private
 **/
Port.prototype.paint=function()
{
  // delegate to the UI representation
  this.uiRepresentation.paint();
}

// prefered direction of the port
//  -1 = direct
//   0 = top
//   1 = right
//   2 = bottom
//   3 = left
Port.prototype.setDirection=function(/*:int*/ direction)
{
  this.direction = direction;
}

/**
 * Returns the default direction of the connection....if any present.
 * @type (int)
  **/
Port.prototype.getDirection=function()
{
  return this.direction;
}

/**
 * Set the position of this port 
 *
 * @param {int} xPos The new x position of the port.
 * @param {int} yPos The new y position of the port.
 **/
Port.prototype.setPosition=function(/*int*/ xPos, /*int*/ yPos)
{
  Rectangle.prototype.setPosition.call(this,xPos,yPos);

  this.originX=xPos; // the fix point of the point.
  this.originY=yPos;

  // Falls das Element noch nie gezeichnet wurde, dann braucht aus das HTML nicht 
  // aktualisiert werden
  //
  if(this.html==null)
    return;


  this.html.style.left = (this.x-this.getWidth()/2)+"px";
  this.html.style.top  = (this.y-this.getHeight()/2)+"px";
}

/**
 * Set the parent of this port.
 * Call {@link Node.addPort} if you want to a port to node. Don't call this method directly.
 *
 * @private
 */
Port.prototype.setParent=function(/*:Node*/ parent)
{
  if(this.parent!=null)
    this.parent.detachMoveListener(this);

  this.parent = parent;
  if(this.parent!=null)
    this.parent.attachMoveListener(this);
}

/**
 * Return the parent {@link Node} of this port.
 * @type (Node)
 **/
Port.prototype.getParent=function()
{
  return this.parent;
}

/**
 * @private
 **/
Port.prototype.onDrag = function()
{
  Rectangle.prototype.onDrag.call(this);

  this.parent.workflow.showConnectionLine(this.parent.x+this.x, this.parent.y+this.y, this.parent.x+this.originX, this.parent.y+this.originY);
}

/**
 * @private
 **/
Port.prototype.onDragend = function()
{
  Rectangle.prototype.onDragend.call(this);

  this.setPosition(this.originX, this.originY);
  this.parent.workflow.hideConnectionLine();
}

/**
 * @private
 **/
Port.prototype.setOrigin=function(/*:int*/ x, /*:int*/ y)
{
  this.originX = x;
  this.originY = y;
}

/**
 * @private
 **/
Port.prototype.onDragEnter = function(/*:Port*/ port)
{
  this.parent.workflow.connectionLine.setColor(new Color(0,150,0));
  this.parent.workflow.connectionLine.setLineWidth(3);
}

/**
 * @private
 **/
Port.prototype.onDragLeave = function(/*:Port*/ port)
{
  this.parent.workflow.connectionLine.setColor(new Color(0,0,0));
  this.parent.workflow.connectionLine.setLineWidth(1);
}

/**
 * @private
 **/
Port.prototype.onDrop = function(/*:Port*/ port)
{
  if(this.parent.id == port.parent.id)
  {
    // same parent -> do nothing
  }
  else
  {
    // OK
    var connection = new Connection();
    connection.setSource(port);
    connection.setTarget(this);
    this.parent.workflow.addFigure(connection);
    if((port.getParent().type=="StateWindow") && (port.type=="OutputPort"))
    {
       this.updateState(port.getParent());
       return;
    }
    if((port.getParent().type=="TransitionWindow") && (port.type=="InputPort"))
    {
       this.updateState(this.getParent());
       return;
    }
    if((port.getParent().type=="TransitionWindow") && (port.type=="OutputPort"))
    {
       this.updateTransition(port.getParent(),this.getParent().title);
       return;
    }
    if((port.getParent().type=="StateWindow") && (port.type=="InputPort"))
    {
       this.updateTransition(this.getParent(),port.getParent().title);
       return;
    }
  }
}

/**
 * Returns the absolute y-position of the port. 
 * @type int
 **/
Port.prototype.getAbsoluteY=function()
{
  return this.originY+ this.parent.getY();
}

/**
 * Returns the absolute x-position of the port. 
 * @type int 
 **/
Port.prototype.getAbsoluteX=function()
{
  return this.originX+this.parent.getX();
}

/**
 * Callback method of the movemoent of a figure
 * @see Figure#attachMoveListener
 * @param {Figure} figure The figure which has been moved
 **/
Port.prototype.onOtherFigureMoved=function(/*:Figure*/ figure)
{
  // Falls sich der parent beweg hat, dann muss der Port dies seinen
  // Connections mitteilen
  this.fireMoveEvent();
}

/**
 * Return the name of this port.
 * @see Node#getPort
 * @type String
 **/
Port.prototype.getName = function()
{
  // wird in einem Property gespeichert, da dieses später via XMLSerializer wird geladen werden muss.
  // Der Serializer kümmert sich allerdings im Moment nur um die Properties.
  return this.getProperty("name");
}

/**
 * Set the name of this port.
 * @see Node#getPort
 * @param {String} name The new name of this port.
 **/
Port.prototype.setName = function(/*:String*/ name)
{
  // wird in einem Property gespeichert, da dieses später via XMLSerializer wird geladen werden muss.
  // Der Serializer kümmert sich allerdings im Moment nur um die Properties.
  this.setProperty("name",name);
}

Port.prototype.updateState=function(state)
{
  var states='';
  var lines = workflow.getLines();
  for(key in lines)
  {
    var line = lines[key];
    if(line!=null && line.type=="Connection" && line.getTarget()!=null)
    {
        if ((line.getTarget().getParent().title==state.title)  && (line.getTarget().type=='OutputPort'))
        {
          states=states+"transitions:list="+line.getSource().getParent().title+"&";
        }
        if ((line.getSource().getParent().title==state.title) && (line.getSource().type=='OutputPort'))
        {
          states=states+"transitions:list="+line.getTarget().getParent().title+"&";
        }
    }
  }
  if (states!='')
  {
    updateStateComplete=function() {
    }
    updateStateFailed=function() { alert('Error. Unable to update transitions.'); }
    updateStateURL="portal_workflow/"+document.location.search.split('=')[1]+"/states/"+state.title+"/updateState?"+states;
    updateState=new Ajax(updateStateURL,{method:'get',onFailure:updateStateFailed,onComplete:updateStateComplete()});
    updateState.request();
  }
}

Port.prototype.updateTransition=function(transition,state)
{
  var transitions='';
  var lines = workflow.getLines();
  for(key in lines)
  {
    var line = lines[key];
    if(line!=null && line.type=="Connection" && line.getTarget()!=null)
    {
        if ((line.getSource().getParent().title==transition.title)  && (line.getSource().type=='OutputPort') && (line.getTarget().getParent().title==state))
        {
          transitions=transitions+"new_state_id="+line.getTarget().getParent().title;
          break;
        }
        if ((line.getTarget().getParent().title==transition.title) && (line.getTarget().type=='InputPort') && (line.getSource().getParent().title==state))
        {
          transitions=transitions+"new_state_id="+line.getSource().getParent().title;
          break;
        }
    }
  }
  if (transitions!='')
  {
    updateTransitionComplete=function() {
    }
    updateTransitionFailed=function() { alert('Error. Unable to update destination state.'); }
    updateTransitionURL="portal_workflow/"+document.location.search.split('=')[1]+"/transitions/"+transition.title+"/updateTransition?"+transitions;
    updateTransition=new Ajax(updateTransitionURL,{method:'get',onFailure:updateTransitionFailed,onComplete:updateTransitionComplete()});
    updateTransition.request();
  }
}
