window.addEvent('domready', function() {
	new Sortables($('test'), {
	 
		initialize: function(){
			var step = 0;
			this.elements.each(function(element, i){
				//var color = [step, 82, 87].hsbToRgb();
				//element.setStyle('background-color', color);
				//step = step + 35;
				//element.setStyle('height', $random(40, 100));
			});
		}
	 
	});
});