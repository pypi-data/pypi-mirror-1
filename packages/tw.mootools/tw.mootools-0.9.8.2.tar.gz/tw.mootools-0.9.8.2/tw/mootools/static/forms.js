function twd_blank_deleted()
{
	tw_grow_undo_data.each(function(g) {
		g.each(function(containers) {
			containers.getElements('input, select, textarea').set('value', '');
		});
	});
}

function twd_suppress_enter(evt) {
	var evt = (evt) ? evt : ((event) ? event : null);
	var node = (evt.target) ? evt.target : ((evt.srcElement) ? evt.srcElement : null);
	if (evt.keyCode == 13) {return node.type == 'textarea';}
}

window.addEvent('domready', function() {
	validated_forms = $$('form.validate_form');
	
	validated_forms.each(function(formelement) {
		new FormCheck(formelement);
	});
});
