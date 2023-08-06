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

function Drag() {}

/**
 * The item currently being dragged.
 * @scope private
 */
Drag.current /*: Draggable */ = null;
Drag.currentTarget /*:DropTarget */=null;

/**
 * Indicates whether or not an item is being dragged.
 * @scope private
 */
Drag.dragging /*: boolean */ = false;

/**
 * Returns true if an item is being dragged.
 * @scope public
 * @return True if an item is being dragged, false if not.
 * @type boolean
 */
Drag.isDragging = function () /*: boolean */ {
    return this.dragging;
};

/**
 * Sets the item being dragged.
 * @scope protected
 * @param {Draggable} oDraggable The draggable item.
 * @type void
 */
Drag.setCurrent = function (oDraggable /*: Draggable */) {
    this.current = oDraggable;
    this.dragging = true;
};

/**
 * Returns the currently dragged item.
 * @scope public
 * @return The currently dragged item.
 * @type Draggable
 */
Drag.getCurrent = function () /*: Draggable */ {
    return this.current;
};

/**
 * Clears the currently dragged item from memory and sets the dragging
 * flag to false.
 * @scope protected
 * @type void
 */
Drag.clearCurrent = function () {
    this.current = null;
    this.dragging = false;
};

/**
 * Encapsulates the functionality for a draggable element.
 * @scope public
 * @extends EventTarget
 * @class
 */
function Draggable(oElement, iConstraints) {

    /*
     * Inherit properties from EventTarget.
     */
    EventTarget.call(this);

    /*
     * Call constructor.
     */
    this.construct(oElement, iConstraints);  

    /**
     * The difference between the x cursor position and left edge of the element.
     * @scope private
     * @type int
     */  
    this.diffX /*: int */ = 0;

    /**
     * The difference between the y cursor position and top edge of the element.
     * @scope private
     * @type int
     */  
    this.diffY /*: int */ = 0;

    /**
     * Collection of drop targets for this item.
     * @scope private
     * @type Array
     */
    this.targets = new Object();
}

/*
 * Inherit methods from EventTarget.
 */
Draggable.prototype = new EventTarget;

/**
 * Indicates the dragged item can be dragged along the X axis.
 * @scope public
 * @type int
 * @final
 */
Draggable.DRAG_X /*: int */ = 1;

/**
 * Indicates the dragged item can be dragged along the Y axis.
 * @scope public
 * @type int
 * @final
 */
Draggable.DRAG_Y /*: int */ = 2;

/**
 * Adds a new drop target to the draggable item.
 * @scope public
 * @param {DropTarget} oDropTarget The drop target to register for this item.
 * @type void
 */
Draggable.prototype.addDropTarget = function (oDropTarget /*: DropTarget */) 
{
    this.targets[oDropTarget.element.id]=oDropTarget0;
};

/**
 * Creates a new instance based on the given element and the constraints.
 * @scope private
 * @constructor
 * @param {HTMLElement} oElement The DOM element to make draggable.
 * @param {int} iConstraints The rules for dragging.
 */
Draggable.prototype.construct = function (oElement /*: HTMLElement */, 
                                           iConstraints /*: int */) {
    /**
     * The element to make draggable.
     * @scope private
     * @type HTMLElement
     */
    this.element /*: HTMLElement */ = oElement;
    
    /**
     * The constraints indicating the rules for dragging.
     * @scope private
     * @type int
     */
    this.constraints /*: int */ = iConstraints;
    
    /*
     * Create a pointer to this object.
     */
    var oThis = this;
    
    var dblTemp = function()
    {
        // Check if the user has made a "double click"
        /*
         * Create a dragstart event and fire it.
         */
        var oDragStartEvent = new DragDropEvent();
        oDragStartEvent.initDragDropEvent("dblclick", true);
        oThis.dispatchEvent(oDragStartEvent);
        var oEvent = arguments[0] || window.event;
        oEvent.cancelBubble = true;
        oEvent.returnValue = false;
      }

    /*
     * Create a temporary function named fnTemp.
     */
    var fnTemp = function () {

        /*
        * Get the event objects, which is either the first
        * argument (for DOM-compliant browsers and Netscape 4.x)
        * or window.event (for IE).
        */
        var oEvent = arguments[0] || window.event;

        // Check if the user has made a "double click"
        /*
         * Create a dragstart event and fire it.
         */
        var oDragStartEvent = new DragDropEvent();
        oDragStartEvent.initDragDropEvent("dragstart", true);
        // dispatch Event benötigt eventuel die x/y Koordinate um zu bestimmen
        // ob dieses Even wirklich relevant ist. (z.b. Wo man in dem Object hinein geklickt hat)
        //
        var scrollLeft= document.body.parentNode.scrollLeft;
        var scrollTop = document.body.parentNode.scrollTop;

        oDragStartEvent.x = oEvent.clientX - oThis.element.offsetLeft+scrollLeft;
        oDragStartEvent.y = oEvent.clientY - oThis.element.offsetTop+scrollTop;
        /*
         * If the event isn't cancelled, proceed.
         */
        if (oThis.dispatchEvent(oDragStartEvent)) 
        {
            /*
             * Get the difference between the clientX and clientY
             * and the position of the element.
             */
            oThis.diffX = oEvent.clientX - oThis.element.offsetLeft;
            oThis.diffY = oEvent.clientY - oThis.element.offsetTop;  

            /*
             * Add all DOM event handlers
             */
            oThis.attachEventHandlers();

            /*
             * Set the currently dragged item.
             */
            Drag.setCurrent(oThis);
        }
        oEvent.cancelBubble = true;
        oEvent.returnValue = false;
    };

    /*
     * Create a temporary function named fnTemp.
     */
    var fnMouseMove = function () 
    {
        // Falls man gerade beim Drag&Drop ist, ist die
        // MouseOver Anzeige ausgeschaltet
        //
        if(Drag.getCurrent()==null)
        {
          /*
          * Get the event objects, which is either the first
          * argument (for DOM-compliant browsers and Netscape 4.x)
          * or window.event (for IE).
          */
          var oEvent = arguments[0] || window.event;
          if(Drag.currentHover!=null && oThis!=Drag.currentHover)
          {
              var oDropEvent = new DragDropEvent();
              oDropEvent.initDragDropEvent("mouseleave", false, oThis);
              Drag.currentHover.dispatchEvent(oDropEvent);
          }
          if(oThis!=null && oThis!=Drag.currentHover)
          {
              var oDropEvent = new DragDropEvent();
              oDropEvent.initDragDropEvent("mouseenter", false, oThis);
              oThis.dispatchEvent(oDropEvent);
          }
          Drag.currentHover = oThis;
  
          oEvent.cancelBubble = true;
          oEvent.returnValue = false;
        }
    };

    /*
     * Determine which method to use to add the event handler.
     */
    if (this.element.addEventListener) {
        this.element.addEventListener("mousemove", fnMouseMove, false);
        this.element.addEventListener("mousedown", fnTemp, false);
        this.element.addEventListener("dblclick", dblTemp, false);
    } else if (this.element.attachEvent) {
        this.element.attachEvent("onmousemove", fnMouseMove);
        this.element.attachEvent("onmousedown", fnTemp);
        this.element.attachEvent("ondblclick", dblTemp);
    } else {
        throw new Error("Drag not supported in this browser.");
    }
};

/**
 * Attaches event handlers for the mousemove and mouseup events.
 * @scope private
 * @private
 * @type void
 */
Draggable.prototype.attachEventHandlers = function () {

    /*
     * Create a pointer to this object.
     */
    var oThis = this;

    /*
     * Create a temporary function named tempMouseMove.
     */
    this.tempMouseMove = function () {

        /*
         * Get the event objects, which is either the first
         * argument (for DOM-compliant browsers and Netscape 4.x)
         * or window.event (for IE).
         */
        var oEvent = arguments[0] || window.event;

        /*
         * Get the new x and y coordinates for the dragged element by
         * subtracting the difference in the x and y direction from 
         * the mouse position on the screen (clientX and clientY).
         */
        var iNewX = oEvent.clientX - oThis.diffX;
        var iNewY = oEvent.clientY - oThis.diffY;

        /*
         * Move the x coordinate if Draggable.DRAG_X is an option.
         */
        if (oThis.constraints & Draggable.DRAG_X) {
            oThis.element.style.left = iNewX+"px";
        }

        /*
         * Move the y coordinate if Draggable.DRAG_Y is an option.
         */
        if (oThis.constraints & Draggable.DRAG_Y) {
            oThis.element.style.top = iNewY+"px";
        }
        var scrollLeft= document.body.parentNode.scrollLeft;
        var scrollTop = document.body.parentNode.scrollTop;
        var oDropTarget  = oThis.getDropTarget(oEvent.clientX+scrollLeft, oEvent.clientY+scrollTop);
        var oCompartment = oThis.getCompartment(oEvent.clientX+scrollLeft, oEvent.clientY+scrollTop);
        if(Drag.currentTarget!=null && oDropTarget!=Drag.currentTarget)
        {
            var oDropEvent = new DragDropEvent();
            oDropEvent.initDragDropEvent("dragleave", false, oThis);
            Drag.currentTarget.dispatchEvent(oDropEvent);
        }
        if(oDropTarget!=null && oDropTarget!=Drag.currentTarget)
        {
            var oDropEvent = new DragDropEvent();
            oDropEvent.initDragDropEvent("dragenter", false, oThis);
            oDropTarget.dispatchEvent(oDropEvent);
        }
        Drag.currentTarget      = oDropTarget;


        if(Drag.currentCompartment!=null && oCompartment!=Drag.currentCompartment)
        {
            var oDropEvent = new DragDropEvent();
            oDropEvent.initDragDropEvent("figureleave", false, oThis);
            Drag.currentCompartment.dispatchEvent(oDropEvent);
        }
        if(oCompartment!=null && oCompartment.node!=oThis.node && oCompartment!=Drag.currentCompartment)
        {
            var oDropEvent = new DragDropEvent();
            oDropEvent.initDragDropEvent("figureenter", false, oThis);
            oCompartment.dispatchEvent(oDropEvent);
        }
        Drag.currentCompartment = oCompartment;

        /*
         * Create and fire a drag event.
         */
        var oDragEvent = new DragDropEvent();
        oDragEvent.initDragDropEvent("drag", false);
        oThis.dispatchEvent(oDragEvent);
    };

    /*
     * Create a temporary function for the mouseup event.
     */
    oThis.tempMouseUp = function () {   

        /*
         * Get the event object.
         */
        var oEvent = arguments[0] || window.event;

        /*
         * Create and fire a dragend event.
         */
        var oDragEndEvent = new DragDropEvent();
        oDragEndEvent.initDragDropEvent("dragend", false);
        oThis.dispatchEvent(oDragEndEvent);

        /*
         * Determine if the mouse is over a drop target.
         */
        var scrollLeft= document.body.parentNode.scrollLeft;
        var scrollTop = document.body.parentNode.scrollTop;
        var oDropTarget = oThis.getDropTarget(oEvent.clientX+scrollLeft, oEvent.clientY+scrollTop);
	var oCompartment= oThis.getCompartment(oEvent.clientX+scrollLeft, oEvent.clientY+scrollTop);
        if (oDropTarget != null) 
        {
            var oDropEvent = new DragDropEvent();
            oDropEvent.initDragDropEvent("drop", false, oThis);
            oDropTarget.dispatchEvent(oDropEvent);
        }
        if (oCompartment != null && oCompartment.node != oThis.node) 
        {
            var oDropEvent = new DragDropEvent();
            oDropEvent.initDragDropEvent("figuredrop", false, oThis);
            oCompartment.dispatchEvent(oDropEvent);
        }

        if(Drag.currentTarget!=null)
        {
            var oDropEvent = new DragDropEvent();
            oDropEvent.initDragDropEvent("dragleave", false, oThis);
            Drag.currentTarget.dispatchEvent(oDropEvent);
            Drag.currentTarget=null;
        }

        Drag.currentCompartment=null;

        /*
         * Clear the currently dragged item.
         */ 
        Drag.clearCurrent();

        /*
         * Detach all of the event handlers.
         */
        oThis.detachEventHandlers();
    };

    /*
     * Determine which method to use to add the event handlers for
     * the mousemove and mouseup events.
     */
    if (document.body.addEventListener) {
        document.body.addEventListener("mousemove", this.tempMouseMove, false);
        document.body.addEventListener("mouseup", this.tempMouseUp, false);
    } else if (document.body.attachEvent) {
        document.body.attachEvent("onmousemove", this.tempMouseMove);
        document.body.attachEvent("onmouseup", this.tempMouseUp);
    } else {
        throw new Error("Drag doesn't support this browser.");
    }
    
};

/**
 * Detaches event handlers for the mousemove and mouseup events.
 * @scope private
 */
Draggable.prototype.detachEventHandlers = function () {

    /*
     * Determine the method for removing the event handlers for the
     * mousemove and mouseup events.
     */
    if (document.body.removeEventListener) {
        document.body.removeEventListener("mousemove", this.tempMouseMove, false);
        document.body.removeEventListener("mouseup", this.tempMouseUp, false);
    } else if (document.body.detachEvent) {
        document.body.detachEvent("onmousemove", this.tempMouseMove);
        document.body.detachEvent("onmouseup", this.tempMouseUp);
    } else {
        throw new Error("Drag doesn't support this browser.");
    }
};

/**
 * Determines the drop target that the mouse is over.
 * @scope private
 * @param x The x-coordinate of the mouse.
 * @param y The y-coordinate of the mouse.
 * @return The drop target if the mouse is over one, null otherwise.
 */
Draggable.prototype.getDropTarget = function (x /*: int */, 
                                              y /*: int */) /*: DropTarget */ {

  for(key in this.targets)
  {
    var target = this.targets[key];
    if (target!=null && target.isOver(x, y) && target.node!=this.node)
    {
        return target;
    }
  }
  return null;
};

/**
 * Determines the compartment target that the mouse is over.
 * @scope private
 * @param x The x-coordinate of the mouse.
 * @param y The y-coordinate of the mouse.
 * @return The drop target if the mouse is over one, null otherwise.
 */
Draggable.prototype.getCompartment = function (x /*: int */, y /*: int */) /*: DropTarget */ {

  for(key in this.node.workflow.compartments)
  {
    var target = this.node.workflow.compartments[key];
    if (target!=null && target.dropable.isOver(x, y) && target!=this.node)
    {
        return target.dropable;
    }
  }
  return null;
};

/**
 * Moves the draggable element to a given position.
 * @scope public
 * @param iX The x-coordinate to move to.
 * @param iY The y-coordinate to move to.
 */
Draggable.prototype.moveTo = function (iX /*: int */, iY /*: int */, smooth) {
    // doIt smooth of fast
    if(!smooth)
    {
	  this.element.style.left = iX + "px";
  	  this.element.style.top = iY + "px";
    }
    else
    {
      // TODO
    }
};


/**
 * Returns the left coordinate of the element.
 * @scope public
 * @return The left coordinate of the element.
 */
Draggable.prototype.getLeft = function () /*: int */ {
    return this.element.offsetLeft;
};

/**
 * Returns the top coordinate of the element.
 * @scope public
 * @return The top coordinate of the element.
 */
Draggable.prototype.getTop = function () /*: int */ {
    return this.element.offsetTop;
};

/**
 * Encapsulates information about a drag drop event.
 * @class
 * @scope public
 * @extends Event
 */
function DragDropEvent() {

    /*
     * Inherit properties from Event.
     */
    Event.call(this);

} 

/*
 * Inherit methods from Event.
 */
DragDropEvent.prototype = new Event();

/**
 * Initializes the event object with information for the event.
 * @scope public
 * @param sType The type of event encapsulated by the object.
 * @param bCancelable True if the event can be cancelled.
 * @param oRelatedTarget The alternate target related to the event.
 */
DragDropEvent.prototype.initDragDropEvent = function(sType /*: String */,
                                                      bCancelable /*: boolean */,
                                                      oRelatedTarget /*: EventTarget */) {
    /*
     * Call inherited method initEvent().
     */
    this.initEvent(sType, bCancelable);

    /*
     * Assign related target (may be null).
     */
    this.relatedTarget = oRelatedTarget;

}

/**
 * A target for a Draggable to be dropped.
 * @scope public
 * @class
 * @extends EventTarget
 */
function DropTarget(oElement) 
{
    /*
     * Inherit properties from EventTarget.
     */
    EventTarget.call(this);

    /*
     * Call constructor.
     */
    this.construct(oElement);
}

/*
 * Inherit methods from EventTarget.
 */
DropTarget.prototype = new EventTarget;

/**
 * Creates a new instance based on the given DOM element.
 * @constructor
 * @scope public
 * @param oElement The DOM element to make into a drop target.
 */
DropTarget.prototype.construct = function (oElement /*: HTMLElement */) 
{
    /**
     * The DOM element to use as a drop target.
     * @scope private
     */
    this.element = oElement;
};

/**
 * Determines if a given set of coordinates is over the element.
 * @scope protected
 * @param iX The x-coordinate to check.
 * @param iY The y-coordinate to check.
 * @return True if the coordinates are over the element, false if not.
 */
DropTarget.prototype.isOver = function (iX /*: int */, iY /*: int */) /*: boolean */ 
{
    var iX1 = this.getLeft();
    var iX2 = iX1 + this.getWidth();
    var iY1 = this.getTop();
    var iY2 = iY1 + this.getHeight();
    return (iX >= iX1 && iX <= iX2 && iY >= iY1 && iY <= iY2);
};

/**
 * Returns the left coordinate of the drop target.
 * @scope public
 * @return The left coordinate of the drop target.
 */
DropTarget.prototype.getLeft = function () /*: int */ {
    var el = this.element;
    var ol=el.offsetLeft;
    while((el=el.offsetParent) != null)
    {
        ol += el.offsetLeft;
    }
    return ol;
};

/**
 * Returns the top coordinate of the drop target.
 * @scope public
 * @return The top coordinate of the drop target.
 */
DropTarget.prototype.getTop = function () /*: int */{
  var el = this.element;
  var ot=el.offsetTop;
  while((el=el.offsetParent) != null)
  {
     ot += el.offsetTop;
  }
  return ot;
};

/**
 * Returns the height of the drop target.
 * @scope public
 * @return The height of the drop target.
 */
DropTarget.prototype.getHeight = function () /*: int */{
    return this.element.offsetHeight;
};

/**
 * Returns the width of the drop target.
 * @scope public
 * @return The width of the drop target.
 */
DropTarget.prototype.getWidth = function () /*: int */{
    return this.element.offsetWidth;
};