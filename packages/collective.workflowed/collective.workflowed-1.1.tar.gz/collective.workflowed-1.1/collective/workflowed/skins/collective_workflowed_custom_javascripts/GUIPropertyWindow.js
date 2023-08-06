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

function VectorPropertyWindow()
{
  PropertyWindow.call(this);

  this.defaultLineColor=new Color(0,0,115);

  this.oldStateChild=null;
  this.oldTransitionChild=null;

  this.setDimension(180,240);
  return this;
}

VectorPropertyWindow.prototype = new PropertyWindow;
VectorPropertyWindow.prototype.type="VectorPropertyWindow";

VectorPropertyWindow.prototype.createHTMLElement=function()
{
  var item = PropertyWindow.prototype.createHTMLElement.call(this);
  
  this.stateDiv = document.createElement('div');
  this.stateDiv.style.position='absolute';
  this.stateDiv.style.top='90';
  this.stateDiv.style.left='15px';

  this.stateLabel = this.createLabel("Possible transitions:", 0,0);
  this.stateDiv.appendChild(this.stateLabel);

  this.stateList = document.createElement("div");
  this.stateDiv.appendChild(this.stateList);

  this.transitionDiv = document.createElement('div');
  this.transitionDiv.style.position='absolute';
  this.transitionDiv.style.top='90';
  this.transitionDiv.style.left='15px';

  this.transitionLabel = this.createLabel("Destination state:", 0,0);
  this.transitionDiv.appendChild(this.transitionLabel);

  this.transitionList = document.createElement("div");
  this.transitionDiv.appendChild(this.transitionList);

  this.stateDiv.style.font="normal 10px verdana";
  this.transitionDiv.style.font="normal 10px verdana";
  this.stateDiv.style.display='none';
  this.transitionDiv.style.display='none';

  this.stateLink= document.createElement("div");
  this.stateLink.innerHTML = '<br />Edit state permissions';
  this.stateLink.style.fontFamily="sans-serif";
  this.stateLink.style.fontSize="8pt";
  this.stateLink.style.color  = "blue";
  this.stateLink.onclick=function() {}
  this.stateDiv.appendChild(this.stateLink);

  this.initialStateLink= document.createElement("div");
  this.initialStateLink.innerHTML = '<br />Set as initial state';
  this.initialStateLink.style.fontFamily="sans-serif";
  this.initialStateLink.style.fontSize="8pt";
  this.initialStateLink.style.color  = "blue";
  this.initialStateLink.onclick=function() {}
  this.stateDiv.appendChild(this.initialStateLink);

  this.transitionLink= document.createElement("div");
  this.transitionLink.innerHTML = '<br />Edit transition properties';
  this.transitionLink.style.fontFamily="sans-serif";
  this.transitionLink.style.fontSize="8pt";
  this.transitionLink.style.color  = "blue";
  this.transitionLink.onclick=function() {}
  this.transitionDiv.appendChild(this.transitionLink);

  item.appendChild(this.stateDiv);
  item.appendChild(this.transitionDiv);

  return item;
}

VectorPropertyWindow.prototype.onSelectionChanged=function(figure /*:Figure*/)
{
  PropertyWindow.prototype.onSelectionChanged.call(this,figure);
  if(Drag.currentHover==null)
    return;
  this.transitionDiv.style.display='none';
  this.stateDiv.style.display='none';
  var lines = workflow.getLines();
  for(key in lines)
  {
    var line = lines[key];
    if(line!=null && line.type=="Connection")
    {
      line.setLineWidth(1);
      line.setColor(this.defaultLineColor);
    }
  }
  if (figure != null && (figure.type == 'StateWindow'))
  {
    this.stateDiv.style.display='block';
    this.transitionDiv.style.display='none';
    stateLinkURL="portal_workflow/"+document.location.search.split('=')[1]+"/states/"+figure.title+"/@@workflowed-state-permissions";
    this.stateLink.onclick=function() {workflow_popup=window.open(stateLinkURL,'workflow_popup','toolbar=0,directories=0,menubar=0,location=0,directories=0,width=700,height=300,scrollbars=1');}
    this.initialStateLink.onclick=function() {
        initialStateComplete=function() {
            figures=figure.canvas.getFigures();
            for(f in figures) {
                if (figures[f].type=='StateWindow') {
                    figures[f].setLineWidth(1);
                }
            }
            figure.setLineWidth(3);
            alert(figure.title+" is now the initial state.");
        }
        initialStateFailed=function() { alert('Error. Unable to update initial state.'); }
        initialStateURL="portal_workflow/"+document.location.search.split('=')[1]+"/states/setInitialState?id="+figure.title;
        initialState=new Ajax(initialStateURL,{method:'get',onFailure:initialStateFailed,onComplete:initialStateComplete()});
        initialState.request();
    }
    stateChild=document.createElement('ul');
    stateChild.style.margin='18px 0 0 0';
    for(key in lines)
    {
      var line = lines[key];
      if(line!=null && line.type=="Connection")
      {
        if ((line.getSource().getParent().title==figure.title)  && (line.getSource().type=='OutputPort'))
        {
          line.setLineWidth(3);
          line.setColor(new Color(245,115,115));
          destination = line.getTarget().getParent().title;
          li=document.createElement('li');
          textNode = document.createTextNode(destination);
          li.appendChild(textNode);
          stateChild.appendChild(li);
        }
        if ((line.getTarget().getParent().title==figure.title) && (line.getTarget().type=='OutputPort'))
        {
          line.setLineWidth(3);
          line.setColor(new Color(245,115,115));
          destination = line.getSource().getParent().title;
          li=document.createElement('li');
          textNode = document.createTextNode(destination);
          li.appendChild(textNode);
          stateChild.appendChild(li);
        }
      }
    }
    if (this.oldStateChild!=null)
      this.stateList.replaceChild(stateChild,this.oldStateChild);
    else
      this.stateList.appendChild(stateChild);
    this.oldStateChild=stateChild;
  }
  if (figure != null && (figure.type == 'TransitionWindow'))
  {
    this.stateDiv.style.display='none';
    this.transitionDiv.style.display='block';
    transitionLinkURL="portal_workflow/"+document.location.search.split('=')[1]+"/transitions/"+figure.title+"/@@workflowed-transition-properties";
    this.transitionLink.onclick=function() {workflow_popup=window.open(transitionLinkURL,'workflow_popup','toolbar=0,directories=0,menubar=0,location=0,directories=0,width=650,height=550,scrollbars=1');}
    transitionChild=document.createElement('ul');
    transitionChild.style.margin='18px 0 0 0';
    for(key in lines)
    {
      var line = lines[key];
      if(line!=null && line.type=="Connection")
      {
        if ((line.getSource().getParent().title==figure.title)  && (line.getSource().type=='OutputPort'))
        {
          line.setLineWidth(3);
          line.setColor(new Color(115,245,115));
          destination = line.getTarget().getParent().title;
          li=document.createElement('li');
          textNode = document.createTextNode(destination);
          li.appendChild(textNode);
          transitionChild.appendChild(li);
        }
        if ((line.getTarget().getParent().title==figure.title) && (line.getTarget().type=='OutputPort'))
        {
          line.setLineWidth(3);
          line.setColor(new Color(115,245,115));
          destination = line.getSource().getParent().title;
          li=document.createElement('li');
          textNode = document.createTextNode(destination);
          li.appendChild(textNode);
          transitionChild.appendChild(li);
        }
      }
    }
    if (this.oldTransitionChild!=null)
      this.transitionList.replaceChild(transitionChild,this.oldTransitionChild);
    else
      this.transitionList.appendChild(transitionChild);
    this.oldTransitionChild=transitionChild;
  }
}

