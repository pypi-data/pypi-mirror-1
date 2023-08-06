/**
 * @fileoverview Defines the Wire class that wraps a canvas tag to create wires.
 */
/**
 * @class The wire widget that uses a canvas to render
 * @extends WireIt.CanvasElement
 * @constructor
 * @param  {WireIt.Terminal}    terminal1   Source terminal
 * @param  {WireIt.Terminal}    terminal2   Target terminal
 * @param  {DomEl}              parentEl    Container of the CANVAS tag
 * @param  {Obj}                config      Styling configuration
 */
WireIt.Wire = function( terminal1, terminal2, parentEl, config) {
   
   /**
    * Reference to the parent dom element
    */
   this.parentEl = parentEl;
   
   /**
    * Reference to the first terminal
    */
   this.terminal1 = terminal1;
   
   /**
    * Reference to the second terminal
    */
   this.terminal2 = terminal2;
   
   /**
    * Wire styling, and properties:
    * <ul>
    *   <li>className: CSS class name of the canvas element (default 'WireIt-Wire')</li>
    *   <li>coeffMulDirection: Parameter for bezier style</li>
    *   <li>cap: default 'round'</li>
    *   <li>bordercap: default 'round'</li>
    *   <li>width: Wire width (default to 3)</li>
    *   <li>borderwidth: Border Width (default to 1)</li>
    *   <li>color: Wire color (default to rgb(173, 216, 230) )</li>
    *   <li>bordercolor: Border color (default to #0000ff )</li>
    * </ul>
    */
   this.config = config || {};
   this.config.className = this.config.className || 'WireIt-Wire';
   this.config.coeffMulDirection = YAHOO.lang.isUndefined(this.config.coeffMulDirection) ? 100 : this.config.coeffMulDirection;
   
   // Syling
   this.config.drawingMethod = this.config.drawingMethod || 'bezier';
   this.config.cap = this.config.cap || 'round';
   this.config.bordercap = this.config.bordercap || 'round';
   this.config.width = this.config.width || 3;
   this.config.borderwidth = this.config.borderwidth || 1;
   /* this.config.color = this.config.color || 'rgb(173, 216, 230)'; */
   this.config.color = this.config.color || '#44bdee';
   this.config.bordercolor = this.config.bordercolor || '#0000ff';
   
   // Create the canvas element
   WireIt.Wire.superclass.constructor.call(this);
   
   this.element.className = this.config.className;
   
   // Append the canvas to the parent element
   this.parentEl.appendChild(this.element);
   
   
   // Call addWire on both terminals
   this.terminal1.addWire(this);
   this.terminal2.addWire(this);
};


YAHOO.lang.extend(WireIt.Wire, WireIt.CanvasElement, 
/**
 * @scope WireIt.Wire.prototype
 */  
{
   /**
    * Remove a Wire from the Dom
    */
   remove: function() {
   
      // Remove the canvas from the dom
      this.parentEl.removeChild(this.element);
   
      // Remove the wire reference from the connected terminals
      if(this.terminal1 && this.terminal1.removeWire) {
         this.terminal1.removeWire(this);
      }
      if(this.terminal2 && this.terminal2.removeWire) {
         this.terminal2.removeWire(this);
      }
   
      // Remove references to old terminals
      this.terminal1 = null;
      this.terminal2 = null;
   },

   /**
    * Redraw the Wire
    */
   drawBezierCurve: function() {
   
      // Get the positions of the terminals
      var p1 = this.terminal1.getXY();
      var p2 = this.terminal2.getXY();
   
      // Coefficient multiplicateur de direction
      // 100 par défaut, si distance(p1,p2) < 100, on passe en distance/2
      var coeffMulDirection=this.config.coeffMulDirection;
   
   
      var distance=Math.sqrt(Math.pow(p1[0]-p2[0],2)+Math.pow(p1[1]-p2[1],2));
      if(distance < coeffMulDirection){
         coeffMulDirection=distance/2;
      }
   
      // Calcul des vecteurs directeurs d1 et d2 :
      var d1=[this.terminal1.config.direction[0]*coeffMulDirection,this.terminal1.config.direction[1]*coeffMulDirection];
      var d2=[this.terminal2.config.direction[0]*coeffMulDirection,this.terminal2.config.direction[1]*coeffMulDirection];
   
      var bezierPoints=[];
      bezierPoints[0]=p1;
      bezierPoints[1]=[p1[0]+d1[0],p1[1]+d1[1]];
      bezierPoints[2]=[p2[0]+d2[0],p2[1]+d2[1]];
      bezierPoints[3]=p2;
      var min=[p1[0],p1[1]];
      var max=[p1[0],p1[1]];
      for(var i=1;i<bezierPoints.length;i++){
         var p=bezierPoints[i];
         if(p[0]<min[0]){
            min[0]=p[0];
         }
         if(p[1]<min[1]){
            min[1]=p[1];
         }
         if(p[0]>max[0]){
            max[0]=p[0];
         }
         if(p[1]>max[1]){
            max[1]=p[1];
         }
      }
      // Redimensionnement du canvas
      var margin=[4,4];
      min[0]=min[0]-margin[0];
      min[1]=min[1]-margin[1];
      max[0]=max[0]+margin[0];
      max[1]=max[1]+margin[1];
      var lw=Math.abs(max[0]-min[0]);
      var lh=Math.abs(max[1]-min[1]);
   
      this.SetCanvasRegion(min[0],min[1],lw,lh);
   
      var ctxt=this.getContext();
      for(var i=0;i<bezierPoints.length;i++){
         bezierPoints[i][0]=bezierPoints[i][0]-min[0];
         bezierPoints[i][1]=bezierPoints[i][1]-min[1];
      }
   
      // Draw the border
      ctxt.lineCap=this.config.bordercap;
      ctxt.strokeStyle=this.config.bordercolor;
      ctxt.lineWidth=this.config.width+this.config.borderwidth*2;
      ctxt.beginPath();
      ctxt.moveTo(bezierPoints[0][0],bezierPoints[0][1]);
      ctxt.bezierCurveTo(bezierPoints[1][0],bezierPoints[1][1],bezierPoints[2][0],bezierPoints[2][1],bezierPoints[3][0],bezierPoints[3][1]);
      ctxt.stroke();
   
      // Draw the inner bezier curve
      ctxt.lineCap=this.config.cap;
      ctxt.strokeStyle=this.config.color;
      ctxt.lineWidth=this.config.width;
      ctxt.beginPath();
      ctxt.moveTo(bezierPoints[0][0],bezierPoints[0][1]);
      ctxt.bezierCurveTo(bezierPoints[1][0],bezierPoints[1][1],bezierPoints[2][0],bezierPoints[2][1],bezierPoints[3][0],bezierPoints[3][1]);
      ctxt.stroke();
   
   },



   /**
    * This function returns terminal1 if the first argument is terminal2 and vice-versa
    * @param   {WireIt.Terminal} terminal    
    * @return  {WireIt.Terminal} terminal    the terminal that is NOT passed as argument
    */
   getOtherTerminal: function(terminal) {
      return (terminal == this.terminal1) ? this.terminal2 : this.terminal1;
   },
   
   
   drawArrows: function()
   {
   	var d = 7; // arrow width/2
      var redim = d+3; //we have to make the canvas a little bigger because of arrows
      var margin=[4+redim,4+redim];

      // Get the positions of the terminals
      var p1 = this.terminal1.getXY();
      var p2 = this.terminal2.getXY();

      var distance=Math.sqrt(Math.pow(p1[0]-p2[0],2)+Math.pow(p1[1]-p2[1],2));

      var min=[ Math.min(p1[0],p2[0])-margin[0], Math.min(p1[1],p2[1])-margin[1]];
      var max=[ Math.max(p1[0],p2[0])+margin[0], Math.max(p1[1],p2[1])+margin[1]];
      
      // Redimensionnement du canvas
      
      var lw=Math.abs(max[0]-min[0])+redim;
      var lh=Math.abs(max[1]-min[1])+redim;

      p1[0]=p1[0]-min[0];
      p1[1]=p1[1]-min[1];
      p2[0]=p2[0]-min[0];
      p2[1]=p2[1]-min[1];

      this.SetCanvasRegion(min[0],min[1],lw,lh);

      var ctxt=this.getContext();
      
      // Draw the border
      ctxt.lineCap=this.config.bordercap;
      ctxt.strokeStyle=this.config.bordercolor;
      ctxt.lineWidth=this.config.width+this.config.borderwidth*2;
      ctxt.beginPath();
      ctxt.moveTo(p1[0],p1[1]);
      ctxt.lineTo(p2[0],p2[1]);
      ctxt.stroke();

      // Draw the inner bezier curve
      ctxt.lineCap=this.config.cap;
      ctxt.strokeStyle=this.config.color;
      ctxt.lineWidth=this.config.width;
      ctxt.beginPath();
      ctxt.moveTo(p1[0],p1[1]);
      ctxt.lineTo(p2[0],p2[1]);
      ctxt.stroke();

   	/* start drawing arrows */

   	var t1 = p1;
   	var t2 = p2;

   	var z = [0,0]; //point on the wire with constant distance (dlug) from terminal2
   	var dlug = 20; //arrow length
   	var t = 1-(dlug/distance);
   	z[0] = Math.abs( t1[0] +  t*(t2[0]-t1[0]) );
   	z[1] = Math.abs( t1[1] + t*(t2[1]-t1[1]) );	

   	//line which connects the terminals: y=ax+b
   	var W = t1[0] - t2[0];
   	var Wa = t1[1] - t2[1];
   	var Wb = t1[0]*t2[1] - t1[1]*t2[0];
   	if (W != 0)
   	{
   		a = Wa/W;
   		b = Wb/W;
   	}
   	else
   	{
   		a = 0;
   	}
   	//line perpendicular to the main line: y = aProst*x + b
   	if (a == 0)
   	{
   		aProst = 0;
   	}
   	else
   	{
   		aProst = -1/a;
   	}
   	bProst = z[1] - aProst*z[0]; //point z lays on this line

   	//we have to calculate coordinates of 2 points, which lay on perpendicular line and have the same distance (d) from point z
   	var A = 1 + Math.pow(aProst,2);
   	var B = 2*aProst*bProst - 2*z[0] - 2*z[1]*aProst;
   	var C = -2*z[1]*bProst + Math.pow(z[0],2) + Math.pow(z[1],2) - Math.pow(d,2) + Math.pow(bProst,2);
   	var delta = Math.pow(B,2) - 4*A*C;
   	if (delta < 0) { return; }
	   
   	var x1 = (-B + Math.sqrt(delta)) / (2*A);
   	var x2 = (-B - Math.sqrt(delta)) / (2*A);	 
   	var y1 = aProst*x1 + bProst;
   	var y2 = aProst*x2 + bProst;
   	
   	if(t1[1] == t2[1]) {
   	      var o = (t1[0] > t2[0]) ? 1 : -1;
      	   x1 = t2[0]+o*dlug;
      	   x2 = x1;
      	   y1 -= d;
      	   y2 += d;
   	}   	

   	//triangle fill
   	ctxt.fillStyle = this.config.color;
   	ctxt.beginPath();
   	ctxt.moveTo(t2[0],t2[1]);
   	ctxt.lineTo(x1,y1);
   	ctxt.lineTo(x2,y2);
   	ctxt.fill();

   	//triangle border	
   	ctxt.strokeStyle = this.config.bordercolor;
   	ctxt.lineWidth = this.config.borderwidth;
   	ctxt.beginPath();
   	ctxt.moveTo(t2[0],t2[1]);
   	ctxt.lineTo(x1,y1);
   	ctxt.lineTo(x2,y2);
   	ctxt.lineTo(t2[0],t2[1]);
   	ctxt.stroke();

   },
   
   drawStraight: function()
   {
   	var d = 7; // arrow width/2
      var redim = d+3; //we have to make the canvas a little bigger because of arrows
      var margin=[4+redim,4+redim];

      // Get the positions of the terminals
      var p1 = this.terminal1.getXY();
      var p2 = this.terminal2.getXY();

      var distance=Math.sqrt(Math.pow(p1[0]-p2[0],2)+Math.pow(p1[1]-p2[1],2));

      var min=[ Math.min(p1[0],p2[0])-margin[0], Math.min(p1[1],p2[1])-margin[1]];
      var max=[ Math.max(p1[0],p2[0])+margin[0], Math.max(p1[1],p2[1])+margin[1]];
      
      // Redimensionnement du canvas
      
      var lw=Math.abs(max[0]-min[0])+redim;
      var lh=Math.abs(max[1]-min[1])+redim;

      p1[0]=p1[0]-min[0];
      p1[1]=p1[1]-min[1];
      p2[0]=p2[0]-min[0];
      p2[1]=p2[1]-min[1];

      this.SetCanvasRegion(min[0],min[1],lw,lh);

      var ctxt=this.getContext();
      
      // Draw the border
      ctxt.lineCap=this.config.bordercap;
      ctxt.strokeStyle=this.config.bordercolor;
      ctxt.lineWidth=this.config.width+this.config.borderwidth*2;
      ctxt.beginPath();
      ctxt.moveTo(p1[0],p1[1]);
      ctxt.lineTo(p2[0],p2[1]);
      ctxt.stroke();

      // Draw the inner bezier curve
      ctxt.lineCap=this.config.cap;
      ctxt.strokeStyle=this.config.color;
      ctxt.lineWidth=this.config.width;
      ctxt.beginPath();
      ctxt.moveTo(p1[0],p1[1]);
      ctxt.lineTo(p2[0],p2[1]);
      ctxt.stroke();
   },
   
   redraw: function() {
      if(this.config.drawingMethod == 'straight') {
         this.drawStraight();
      }
      else if(this.config.drawingMethod == 'arrows') {
         this.drawArrows();
      }
      else if(this.config.drawingMethod == 'bezier') {
         this.drawBezierCurve();
      }
      else {
         throw new Error("WireIt.Wire unable to find '"+this.drawingMethod+"' drawing method.");
      }
   }


});

