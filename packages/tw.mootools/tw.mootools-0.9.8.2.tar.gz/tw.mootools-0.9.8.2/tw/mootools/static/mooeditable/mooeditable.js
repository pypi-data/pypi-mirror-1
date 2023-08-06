 
/*
---

script: MooEditable.js

description: Class for creating a WYSIWYG editor, for contentEditable-capable browsers.

license: MIT-style license

authors:
- Lim Chee Aun
- Radovan Lozej
- Ryan Mitchell
- Olivier Refalo
- T.J. Leahy

requires:
- core:1.2.4/Events
- core:1.2.4/Options
- core:1.2.4/Element.Event
- core:1.2.4/Element.Style
- core:1.2.4/Element.Dimensions
- core:1.2.4/Selectors

inspiration:
- Code inspired by Stefan's work [Safari Supports Content Editing!](http://www.xs4all.nl/~hhijdra/stefan/ContentEditable.html) from [safari gets contentEditable](http://walkah.net/blog/walkah/safari-gets-contenteditable)
- Main reference from Peter-Paul Koch's [execCommand compatibility](http://www.quirksmode.org/dom/execCommand.html)
- Some ideas and code inspired by [TinyMCE](http://tinymce.moxiecode.com/)
- Some functions inspired by Inviz's [Most tiny wysiwyg you ever seen](http://forum.mootools.net/viewtopic.php?id=746), [mooWyg (Most tiny WYSIWYG 2.0)](http://forum.mootools.net/viewtopic.php?id=5740)
- Some regex from Cameron Adams's [widgEditor](http://widgeditor.googlecode.com/)
- Some code from Juan M Martinez's [jwysiwyg](http://jwysiwyg.googlecode.com/)
- Some reference from MoxieForge's [PunyMCE](http://punymce.googlecode.com/)
- IE support referring Robert Bredlau's [Rich Text Editing](http://www.rbredlau.com/drupal/node/6)
- Tango icons from the [Tango Desktop Project](http://tango.freedesktop.org/)
- Additional Tango icons from Jimmacs' [Tango OpenOffice](http://www.gnome-look.org/content/show.php/Tango+OpenOffice?content=54799)

provides: [MooEditable, MooEditable.Selection, MooEditable.UI, MooEditable.Actions]

...
*/

(function(){
	
var blockEls = /^(H[1-6]|HR|P|DIV|ADDRESS|PRE|FORM|TABLE|LI|OL|UL|TD|CAPTION|BLOCKQUOTE|CENTER|DL|DT|DD)$/i;
var urlRegex = /^(https?|ftp|rmtp|mms):\/\/(([A-Z0-9][A-Z0-9_-]*)(\.[A-Z0-9][A-Z0-9_-]*)+)(:(\d+))?\/?/i;

this.MooEditable = new Class({

	Implements: [Events, Options],

	options: {
		toolbar: true,
		cleanup: true,
		paragraphise: true,
		xhtml : true,
		semantics : true,
		actions: 'bold italic underline strikethrough | insertunorderedlist insertorderedlist indent outdent | undo redo | createlink unlink | urlimage | toggleview',
		handleSubmit: true,
		handleLabel: true,
		baseCSS: 'html{ height: 100%; cursor: text; } body{ font-family: sans-serif; }',
		extraCSS: '',
		externalCSS: '',
		html: '<!DOCTYPE html><html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><style>{BASECSS} {EXTRACSS}</style>{EXTERNALCSS}</head><body>{CONTENT}</body></html>',
		rootElement: 'p'
	},

	initialize: function(el, options){
		this.setOptions(options);
		this.textarea = document.id(el);
		this.textarea.store('MooEditable', this);
		this.actions = this.options.actions.clean().split(' ');
		this.keys = {};
		this.dialogs = {};
		this.actions.each(function(action){
			var act = MooEditable.Actions[action];
			if (!act) return;
			if (act.options){
				var key = act.options.shortcut;
				if (key) this.keys[key] = action;
			}
			if (act.dialogs){
				$each(act.dialogs, function(dialog, name){
					dialog = dialog.attempt(this);
					dialog.name = action + ':' + name;
					if ($type(this.dialogs[action]) != 'object') this.dialogs[action] = {};
					this.dialogs[action][name] = dialog;
				}, this);
			}
			if (act.events){
				$each(act.events, function(fn, event){
					this.addEvent(event, fn);
				}, this);
			}
		}.bind(this));
		this.render();
	},
	
	toElement: function(){
		return this.textarea;
	},
	
	render: function(){
		var self = this;
		
		// Dimensions
		var dimensions = this.textarea.getSize();
		
		// Build the container
		this.container = new Element('div', {
			id: (this.textarea.id) ? this.textarea.id + '-mooeditable-container' : null,
			'class': 'mooeditable-container',
			styles: {
				width: dimensions.x
			}
		});

		// Override all textarea styles
		this.textarea.addClass('mooeditable-textarea').setStyle('height', dimensions.y);
		
		// Build the iframe
		this.iframe = new IFrame({
			'class': 'mooeditable-iframe',
			frameBorder: 0,
			src: 'javascript:""', // Workaround for HTTPs warning in IE6/7
			styles: {
				height: dimensions.y
			}
		});
		
		this.toolbar = new MooEditable.UI.Toolbar({
			onItemAction: function(){
				var args = $splat(arguments);
				var item = args[0];
				self.action(item.name, args);
			}
		});
		this.attach.delay(1, this);
		
		// Update the event for textarea's corresponding labels
		if (this.options.handleLabel && this.textarea.id) $$('label[for="'+this.textarea.id+'"]').addEvent('click', function(e){
			if (self.mode != 'iframe') return;
			e.preventDefault();
			self.focus();
		});

		// Update & cleanup content before submit
		if (this.options.handleSubmit){
			this.form = this.textarea.getParent('form');
			if (!this.form) return;
			this.form.addEvent('submit', function(){
				if (self.mode == 'iframe') self.saveContent();
			});
		}
		
		this.fireEvent('render', this);
	},

	attach: function(){
		var self = this;

		// Assign view mode
		this.mode = 'iframe';
		
		// Editor iframe state
		this.editorDisabled = false;

		// Put textarea inside container
		this.container.wraps(this.textarea);

		this.textarea.setStyle('display', 'none');
		
		this.iframe.setStyle('display', '').inject(this.textarea, 'before');
		
		$each(this.dialogs, function(action, name){
			$each(action, function(dialog){
				document.id(dialog).inject(self.iframe, 'before');
				var range;
				dialog.addEvents({
					open: function(){
						range = self.selection.getRange();
						self.editorDisabled = true;
						self.toolbar.disable(name);
						self.fireEvent('dialogOpen', this);
					},
					close: function(){
						self.toolbar.enable();
						self.editorDisabled = false;
						self.focus();
						if (range) self.selection.setRange(range);
						self.fireEvent('dialogClose', this);
					}
				});
			});
		});

		// contentWindow and document references
		this.win = this.iframe.contentWindow;
		this.doc = this.win.document;

		// Build the content of iframe
		var docHTML = this.options.html.substitute({
			BASECSS: this.options.baseCSS,
			EXTRACSS: this.options.extraCSS,
			EXTERNALCSS: (this.options.externalCSS) ? '<link rel="stylesheet" href="' + this.options.externalCSS + '">': '',
			CONTENT: this.cleanup(this.textarea.get('value'))
		});
		this.doc.open();
		this.doc.write(docHTML);
		this.doc.close();

		// Turn on Design Mode
		// IE fired load event twice if designMode is set
		(Browser.Engine.trident) ? this.doc.body.contentEditable = true : this.doc.designMode = 'On';

		// Mootoolize window, document and body
		if (!this.win.$family) new Window(this.win);
		if (!this.doc.$family) new Document(this.doc);
		document.id(this.doc.body);

		// Bind all events
		this.doc.addEvents({
			mouseup: this.editorMouseUp.bind(this),
			mousedown: this.editorMouseDown.bind(this),
			mouseover: this.editorMouseOver.bind(this),
			mouseout: this.editorMouseOut.bind(this),
			mouseenter: this.editorMouseEnter.bind(this),
			mouseleave: this.editorMouseLeave.bind(this),
			contextmenu: this.editorContextMenu.bind(this),
			click: this.editorClick.bind(this),
			dbllick: this.editorDoubleClick.bind(this),
			keypress: this.editorKeyPress.bind(this),
			keyup: this.editorKeyUp.bind(this),
			keydown: this.editorKeyDown.bind(this),
			focus: this.editorFocus.bind(this),
			blur: this.editorBlur.bind(this)
		});
		['cut', 'copy', 'paste'].each(function(event){
			self.doc.body.addListener(event, self['editor' + event.capitalize()].bind(self));
		});
		this.textarea.addEvent('keypress', this.textarea.retrieve('mooeditable:textareaKeyListener', this.keyListener.bind(this)));
		
		// Fix window focus event not firing on Firefox 2
		if (Browser.Engine.gecko && Browser.Engine.version == 18) this.doc.addEvent('focus', function(){
			self.win.fireEvent('focus').focus();
		});

		// styleWithCSS, not supported in IE and Opera
		if (!(/trident|presto/i).test(Browser.Engine.name)){
			var styleCSS = function(){
				self.execute('styleWithCSS', false, false);
				self.doc.removeEvent('focus', styleCSS);
			};
			this.win.addEvent('focus', styleCSS);
		}

		if (this.options.toolbar){
			document.id(this.toolbar).inject(this.container, 'top');
			this.toolbar.render(this.actions);
		}

		this.selection = new MooEditable.Selection(this.win);
		
		this.oldContent = this.getContent();
		
		this.fireEvent('attach', this);
		
		return this;
	},
	
	detach: function(){
		this.saveContent();
		this.textarea.setStyle('display', '').removeClass('mooeditable-textarea').inject(this.container, 'before');
		this.textarea.removeEvent('keypress', this.textarea.retrieve('mooeditable:textareaKeyListener'));
		this.container.dispose();
		this.fireEvent('detach', this);
		return this;
	},
	
	editorFocus: function(e){
		this.oldContent = '';
		this.fireEvent('editorFocus', [e, this]);
	},
	
	editorBlur: function(e){
		this.oldContent = this.saveContent().getContent();
		this.fireEvent('editorBlur', [e, this]);
	},
	
	editorMouseUp: function(e){
		if (this.editorDisabled){
			e.stop();
			return;
		}
		
		if (this.options.toolbar) this.checkStates();
		
		this.fireEvent('editorMouseUp', [e, this]);
	},
	
	editorMouseDown: function(e){
		if (this.editorDisabled){
			e.stop();
			return;
		}
		
		this.fireEvent('editorMouseDown', [e, this]);
	},
	
	editorMouseOver: function(e){
		if (this.editorDisabled){
			e.stop();
			return;
		}
		
		this.fireEvent('editorMouseOver', [e, this]);
	},
	
	editorMouseOut: function(e){
		if (this.editorDisabled){
			e.stop();
			return;
		}
		
		this.fireEvent('editorMouseOut', [e, this]);
	},
	
	editorMouseEnter: function(e){
		if (this.editorDisabled){
			e.stop();
			return;
		}
		
		if (this.oldContent && this.getContent() != this.oldContent){
			this.focus();
			this.fireEvent('editorPaste', [e, this]);
		}
		
		this.fireEvent('editorMouseEnter', [e, this]);
	},
	
	editorMouseLeave: function(e){
		if (this.editorDisabled){
			e.stop();
			return;
		}
		
		this.fireEvent('editorMouseLeave', [e, this]);
	},
	
	editorContextMenu: function(e){
		if (this.editorDisabled){
			e.stop();
			return;
		}
		
		this.fireEvent('editorContextMenu', [e, this]);
	},
	
	editorClick: function(e){
		// make images selectable and draggable in Safari
		if (Browser.Engine.webkit){
			var el = e.target;
			if (el.get('tag') == 'img'){
				this.selection.selectNode(el);
			}
		}
		
		this.fireEvent('editorClick', [e, this]);
	},
	
	editorDoubleClick: function(e){
		this.fireEvent('editorDoubleClick', [e, this]);
	},
	
	editorKeyPress: function(e){
		if (this.editorDisabled){
			e.stop();
			return;
		}
		
		this.keyListener(e);
		
		this.fireEvent('editorKeyPress', [e, this]);
	},
	
	editorKeyUp: function(e){
		if (this.editorDisabled){
			e.stop();
			return;
		}
		
		var c = e.code;
		// 33-36 = pageup, pagedown, end, home; 45 = insert
		if (this.options.toolbar && (/^enter|left|up|right|down|delete|backspace$/i.test(e.key) || (c >= 33 && c <= 36) || c == 45 || e.meta || e.control)){
			if (Browser.Engines.trident4){ // Delay for less cpu usage when you are typing
				$clear(this.checkStatesDelay);
				this.checkStatesDelay = this.checkStates.delay(500, this);
			} else {
				this.checkStates();
			}
		}
		
		this.fireEvent('editorKeyUp', [e, this]);
	},
	
	editorKeyDown: function(e){
		if (this.editorDisabled){
			e.stop();
			return;
		}
		
		if (e.key == 'enter'){
			if (this.options.paragraphise){
				if (e.shift && Browser.Engine.webkit){
					var s = this.selection;
					var r = s.getRange();
					
					// Insert BR element
					var br = this.doc.createElement('br');
					r.insertNode(br);
					
					// Place caret after BR
					r.setStartAfter(br);
					r.setEndAfter(br);
					s.setRange(r);
					
					// Could not place caret after BR then insert an nbsp entity and move the caret
					if (s.getSelection().focusNode == br.previousSibling){
						var nbsp = this.doc.createTextNode('\u00a0');
						var p = br.parentNode;
						var ns = br.nextSibling;
						(ns) ? p.insertBefore(nbsp, ns) : p.appendChild(nbsp);
						s.selectNode(nbsp);
						s.collapse(1);
					}
					
					// Scroll to new position, scrollIntoView can't be used due to bug: http://bugs.webkit.org/show_bug.cgi?id=16117
					this.win.scrollTo(0, Element.getOffsets(s.getRange().startContainer).y);
					
					e.preventDefault();
				} else if (Browser.Engine.gecko || Browser.Engine.webkit){
					var node = this.selection.getNode();
					var isBlock = node.getParents().include(node).some(function(el){
						return el.nodeName.test(blockEls);
					});
					if (!isBlock) this.execute('insertparagraph');
				}
			} else {
				if (Browser.Engine.trident){
					var r = this.selection.getRange();
					var node = this.selection.getNode();
					if (r && node.get('tag') != 'li'){
						this.selection.insertContent('<br>');
						this.selection.collapse(false);
					}
					e.preventDefault();
				}
			}
		}
		
		if (Browser.Engine.presto){
			var ctrlmeta = e.control || e.meta;
			if (ctrlmeta && e.key == 'x'){
				this.fireEvent('editorCut', [e, this]);
			} else if (ctrlmeta && e.key == 'c'){
				this.fireEvent('editorCopy', [e, this]);
			} else if ((ctrlmeta && e.key == 'v') || (e.shift && e.code == 45)){
				this.fireEvent('editorPaste', [e, this]);
			}
		}
		
		this.fireEvent('editorKeyDown', [e, this]);
	},
	
	editorCut: function(e){
		if (this.editorDisabled){
			e.stop();
			return;
		}
		
		this.fireEvent('editorCut', [e, this]);
	},
	
	editorCopy: function(e){
		if (this.editorDisabled){
			e.stop();
			return;
		}
		
		this.fireEvent('editorCopy', [e, this]);
	},
	
	editorPaste: function(e){
		if (this.editorDisabled){
			e.stop();
			return;
		}
		
		this.fireEvent('editorPaste', [e, this]);
	},
	
	keyListener: function(e){
		var key = (Browser.Platform.mac) ? e.meta : e.control;
		if (!key || !this.keys[e.key]) return;
		e.preventDefault();
		var item = this.toolbar.getItem(this.keys[e.key]);
		item.action(e);
	},

	focus: function(){
		(this.mode == 'iframe' ? this.win : this.textarea).focus();
		this.fireEvent('focus', this);
		return this;
	},

	action: function(command, args){
		var action = MooEditable.Actions[command];
		if (action.command && $type(action.command) == 'function'){
			action.command.run(args, this);
		} else {
			this.focus();
			this.execute(command, false, args);
			if (this.mode == 'iframe') this.checkStates();
		}
	},

	execute: function(command, param1, param2){
		if (this.busy) return;
		this.busy = true;
		this.doc.execCommand(command, param1, param2);
		this.saveContent();
		this.busy = false;
		return false;
	},

	toggleView: function(){
		this.fireEvent('beforeToggleView', this);
		if (this.mode == 'textarea'){
			this.mode = 'iframe';
			this.iframe.setStyle('display', '');
			this.setContent(this.textarea.value);
			this.textarea.setStyle('display', 'none');
		} else {
			this.saveContent();
			this.mode = 'textarea';
			this.textarea.setStyle('display', '');
			this.iframe.setStyle('display', 'none');
		}
		this.fireEvent('toggleView', this);
		this.focus.delay(10, this);
		return this;
	},

	getContent: function(){
		return this.cleanup(this.doc.body.get('html'));
	},

	setContent: function(newContent){
		this.doc.body.set('html', this.ensureRootElement(newContent));
		return this;
	},

	saveContent: function(){
		if (this.mode == 'iframe'){
			this.textarea.set('value', this.ensureRootElement(this.getContent()));
		}
		return this;
	},
	
	ensureRootElement: function(val){
		if (this.options.rootElement){
			var el = new Element('div', {html: val.trim()});
			var start = -1;
			var create = false;
			var html = '';
			var length = el.childNodes.length;
			for (i=0; i<length; i++){
				var childNode = el.childNodes[i];
				var nodeName = childNode.nodeName;
				if (!nodeName.test(blockEls) && nodeName !== '#comment'){
					if (nodeName === '#text'){
						if (childNode.nodeValue.trim()){
							if (start < 0) start = i;
							html += childNode.nodeValue;
						}
					} else {
						if (start < 0) start = i;
						html += new Element('div').adopt($(childNode).clone()).get('html');
					}
				} else {
					create = true;
				}
				if (i == (length-1)) create = true;
				if (start >= 0 && create){
					var newel = new Element(this.options.rootElement, {html: html});
					el.replaceChild(newel, el.childNodes[start]);
					for (k=start+1; k<=i; k++){ 
						el.removeChild(el.childNodes[k]);
						length--;
						i--;
						k--;
					}
					start = -1;
					create = false;
					html = '';
				}
			}
			val = el.get('html').replace(/\n\n/g, '');
		}
		return val;
	},

	checkStates: function(){
		var element = this.selection.getNode();
		if (!element) return;
		if ($type(element) != 'element') return;
		
		this.actions.each(function(action){
			var item = this.toolbar.getItem(action);
			if (!item) return;
			item.deactivate();

			var states = MooEditable.Actions[action]['states'];
			if (!states) return;
			
			// custom checkState
			if ($type(states) == 'function'){
				states.attempt([document.id(element), item], this);
				return;
			}
			
			try{
				if (this.doc.queryCommandState(action)){
					item.activate();
					return;
				}
			} catch(e){}
			
			if (states.tags){
				var el = element;
				do {
					var tag = el.tagName.toLowerCase();
					if (states.tags.contains(tag)){
						item.activate(tag);
						break;
					}
				}
				while ((el = Element.getParent(el)) != null);
			}

			if (states.css){
				var el = element;
				do {
					var found = false;
					for (var prop in states.css){
						var css = states.css[prop];
						if (Element.getStyle(el, prop).contains(css)){
							item.activate(css);
							found = true;
						}
					}
					if (found || el.tagName.test(blockEls)) break;
				}
				while ((el = Element.getParent(el)) != null);
			}
		}.bind(this));
	},

	cleanup: function(source){
		if (!this.options.cleanup) return source.trim();
		
		do {
			var oSource = source;

			// Webkit cleanup
			source = source.replace(/<br class\="webkit-block-placeholder">/gi, "<br />");
			source = source.replace(/<span class="Apple-style-span">(.*)<\/span>/gi, '$1');
			source = source.replace(/ class="Apple-style-span"/gi, '');
			source = source.replace(/<span style="">/gi, '');

			// Remove padded paragraphs
			source = source.replace(/<p>\s*<br ?\/?>\s*<\/p>/gi, '<p>\u00a0</p>');
			source = source.replace(/<p>(&nbsp;|\s)*<\/p>/gi, '<p>\u00a0</p>');
			if (!this.options.semantics){
				source = source.replace(/\s*<br ?\/?>\s*<\/p>/gi, '</p>');
			}

			// Replace improper BRs (only if XHTML : true)
			if (this.options.xhtml){
				source = source.replace(/<br>/gi, "<br />");
			}

			if (this.options.semantics){
				//remove divs from <li>
				if (Browser.Engine.trident){
					source = source.replace(/<li>\s*<div>(.+?)<\/div><\/li>/g, '<li>$1</li>');
				}
				//remove stupid apple divs
				if (Browser.Engine.webkit){
					source = source.replace(/^([\w\s]+.*?)<div>/i, '<p>$1</p><div>');
					source = source.replace(/<div>(.+?)<\/div>/ig, '<p>$1</p>');
				}

				//<p> tags around a list will get moved to after the list
				if (['gecko', 'presto', 'webkit'].contains(Browser.Engine.name)){
					//not working properly in safari?
					source = source.replace(/<p>[\s\n]*(<(?:ul|ol)>.*?<\/(?:ul|ol)>)(.*?)<\/p>/ig, '$1<p>$2</p>');
					source = source.replace(/<\/(ol|ul)>\s*(?!<(?:p|ol|ul|img).*?>)((?:<[^>]*>)?\w.*)$/g, '</$1><p>$2</p>');
				}

				source = source.replace(/<br[^>]*><\/p>/g, '</p>'); // remove <br>'s that end a paragraph here.
				source = source.replace(/<p>\s*(<img[^>]+>)\s*<\/p>/ig, '$1\n'); // if a <p> only contains <img>, remove the <p> tags

				//format the source
				source = source.replace(/<p([^>]*)>(.*?)<\/p>(?!\n)/g, '<p$1>$2</p>\n'); // break after paragraphs
				source = source.replace(/<\/(ul|ol|p)>(?!\n)/g, '</$1>\n'); // break after </p></ol></ul> tags
				source = source.replace(/><li>/g, '>\n\t<li>'); // break and indent <li>
				source = source.replace(/([^\n])<\/(ol|ul)>/g, '$1\n</$2>'); //break before </ol></ul> tags
				source = source.replace(/([^\n])<img/ig, '$1\n<img'); // move images to their own line
				source = source.replace(/^\s*$/g, ''); // delete empty lines in the source code (not working in opera)
			}

			// Remove leading and trailing BRs
			source = source.replace(/<br ?\/?>$/gi, '');
			source = source.replace(/^<br ?\/?>/gi, '');

			// Remove useless BRs
			source = source.replace(/><br ?\/?>/gi, '>');

			// Remove BRs right before the end of blocks
			source = source.replace(/<br ?\/?>\s*<\/(h1|h2|h3|h4|h5|h6|li|p)/gi, '</$1');

			// Semantic conversion
			source = source.replace(/<span style="font-weight: bold;">(.*)<\/span>/gi, '<strong>$1</strong>');
			source = source.replace(/<span style="font-style: italic;">(.*)<\/span>/gi, '<em>$1</em>');
			source = source.replace(/<b\b[^>]*>(.*?)<\/b[^>]*>/gi, '<strong>$1</strong>');
			source = source.replace(/<i\b[^>]*>(.*?)<\/i[^>]*>/gi, '<em>$1</em>');
			source = source.replace(/<u\b[^>]*>(.*?)<\/u[^>]*>/gi, '<span style="text-decoration: underline;">$1</span>');
			source = source.replace(/<strong><span style="font-weight: normal;">(.*)<\/span><\/strong>/gi, '$1');
			source = source.replace(/<em><span style="font-weight: normal;">(.*)<\/span><\/em>/gi, '$1');
			source = source.replace(/<span style="text-decoration: underline;"><span style="font-weight: normal;">(.*)<\/span><\/span>/gi, '$1');
			source = source.replace(/<strong style="font-weight: normal;">(.*)<\/strong>/gi, '$1');
			source = source.replace(/<em style="font-weight: normal;">(.*)<\/em>/gi, '$1');

			// Replace uppercase element names with lowercase
			source = source.replace(/<[^> ]*/g, function(match){return match.toLowerCase();});

			// Replace uppercase attribute names with lowercase
			source = source.replace(/<[^>]*>/g, function(match){
				   match = match.replace(/ [^=]+=/g, function(match2){return match2.toLowerCase();});
				   return match;
			});

			// Put quotes around unquoted attributes
			source = source.replace(/<[^>]*>/g, function(match){
				   match = match.replace(/( [^=]+=)([^"][^ >]*)/g, "$1\"$2\"");
				   return match;
			});

			//make img tags xhtml compatible <img>,<img></img> -> <img/>
			if (this.options.xhtml){
				source = source.replace(/<img([^>]+)(\s*[^\/])>(<\/img>)*/gi, '<img$1$2 />');
			}
			
			//remove double <p> tags and empty <p> tags
			source = source.replace(/<p>(?:\s*)<p>/g, '<p>');
			source = source.replace(/<\/p>\s*<\/p>/g, '</p>');
			
			// Replace <br>s inside <pre> automatically added by some browsers
			source = source.replace(/<pre[^>]*>.*?<\/pre>/gi, function(match){
				return match.replace(/<br ?\/?>/gi, '\n');
			});

			// Final trim
			source = source.trim();
		}
		while (source != oSource);

		return source;
	}

});

MooEditable.Selection = new Class({

	initialize: function(win){
		this.win = win;
	},

	getSelection: function(){
		this.win.focus();
		return (this.win.getSelection) ? this.win.getSelection() : this.win.document.selection;
	},

	getRange: function(){
		var s = this.getSelection();

		if (!s) return null;

		try {
			return s.rangeCount > 0 ? s.getRangeAt(0) : (s.createRange ? s.createRange() : null);
		} catch(e) {
			// IE bug when used in frameset
			return this.doc.body.createTextRange();
		}
	},

	setRange: function(range){
		if (range.select){
			$try(function(){
				range.select();
			});
		} else {
			var s = this.getSelection();
			if (s.addRange){
				s.removeAllRanges();
				s.addRange(range);
			}
		}
	},

	selectNode: function(node, collapse){
		var r = this.getRange();
		var s = this.getSelection();

		if (r.moveToElementText){
			$try(function(){
				r.moveToElementText(node);
				r.select();
			});
		} else if (s.addRange){
			collapse ? r.selectNodeContents(node) : r.selectNode(node);
			s.removeAllRanges();
			s.addRange(r);
		} else {
			s.setBaseAndExtent(node, 0, node, 1);
		}

		return node;
	},

	isCollapsed: function(){
		var r = this.getRange();
		if (r.item) return false;
		return r.boundingWidth == 0 || this.getSelection().isCollapsed;
	},

	collapse: function(toStart){
		var r = this.getRange();
		var s = this.getSelection();

		if (r.select){
			r.collapse(toStart);
			r.select();
		} else {
			toStart ? s.collapseToStart() : s.collapseToEnd();
		}
	},

	getContent: function(){
		var r = this.getRange();
		var body = new Element('body');

		if (this.isCollapsed()) return '';

		if (r.cloneContents){
			body.appendChild(r.cloneContents());
		} else if ($defined(r.item) || $defined(r.htmlText)){
			body.set('html', r.item ? r.item(0).outerHTML : r.htmlText);
		} else {
			body.set('html', r.toString());
		}

		var content = body.get('html');
		return content;
	},

	getText : function(){
		var r = this.getRange();
		var s = this.getSelection();
		return this.isCollapsed() ? '' : r.text || (s.toString ? s.toString() : '');
	},

	getNode: function(){
		var r = this.getRange();

		if (!Browser.Engine.trident){
			var el = null;

			if (r){
				el = r.commonAncestorContainer;

				// Handle selection a image or other control like element such as anchors
				if (!r.collapsed)
					if (r.startContainer == r.endContainer)
						if (r.startOffset - r.endOffset < 2)
							if (r.startContainer.hasChildNodes())
								el = r.startContainer.childNodes[r.startOffset];

				while ($type(el) != 'element') el = el.parentNode;
			}

			return document.id(el);
		}

		return document.id(r.item ? r.item(0) : r.parentElement());
	},

	insertContent: function(content){
		if (Browser.Engine.trident){
			var r = this.getRange();
			r.pasteHTML(content);
			r.collapse(false);
			r.select();
		} else {
			this.win.document.execCommand('insertHTML', false, content);
		}
	}

});

MooEditable.UI = {};

MooEditable.UI.Toolbar= new Class({

	Implements: [Events, Options],

	options: {
		/*
		onItemAction: $empty,
		*/
		'class': ''
	},
    
	initialize: function(options){
		this.setOptions(options);
		this.el = new Element('div', {'class': 'mooeditable-ui-toolbar ' + this.options['class']});
		this.items = {};
		this.content = null;
	},
	
	toElement: function(){
		return this.el;
	},
	
	render: function(actions){
		if (this.content){
			this.el.adopt(this.content);
		} else {
			this.content = actions.map(function(action){
				return (action == '|') ? this.addSeparator() : this.addItem(action);
			}.bind(this));
		}
		return this;
	},
	
	addItem: function(action){
		var self = this;
		var act = MooEditable.Actions[action];
		if (!act) return;
		var type = act.type || 'button';
		var options = act.options || {};
		var item = new MooEditable.UI[type.camelCase().capitalize()]($extend(options, {
			name: action,
			'class': action + '-item toolbar-item',
			title: act.title,
			onAction: self.itemAction.bind(self)
		}));
		this.items[action] = item;
		document.id(item).inject(this.el);
		return item;
	},
	
	getItem: function(action){
		return this.items[action];
	},
	
	addSeparator: function(){
		return new Element('span', {'class': 'toolbar-separator'}).inject(this.el);
	},
	
	itemAction: function(){
		this.fireEvent('itemAction', arguments);
	},

	disable: function(except){
		$each(this.items, function(item){
			(item.name == except) ? item.activate() : item.deactivate().disable();
		});
		return this;
	},

	enable: function(){
		$each(this.items, function(item){
			item.enable();
		});
		return this;
	},
	
	show: function(){
		this.el.setStyle('display', '');
		return this;
	},
	
	hide: function(){
		this.el.setStyle('display', 'none');
		return this;
	}
	
});

MooEditable.UI.Button = new Class({

	Implements: [Events, Options],

	options: {
		/*
		onAction: $empty,
		*/
		title: '',
		name: '',
		text: 'Button',
		'class': '',
		shortcut: '',
		mode: 'icon'
	},

	initialize: function(options){
		this.setOptions(options);
		this.name = this.options.name;
		this.render();
	},
	
	toElement: function(){
		return this.el;
	},
	
	render: function(){
		var self = this;
		var key = (Browser.Platform.mac) ? 'Cmd' : 'Ctrl';
		var shortcut = (this.options.shortcut) ? ' ( ' + key + '+' + this.options.shortcut.toUpperCase() + ' )' : '';
		var text = this.options.title || name;
		var title = text + shortcut;
		this.el = new Element('button', {
			'class': 'mooeditable-ui-button ' + self.options['class'],
			title: title,
			html: '<span class="button-icon"></span><span class="button-text">' + text + '</span>',
			events: {
				click: self.click.bind(self),
				mousedown: function(e){ e.preventDefault(); }
			}
		});
		if (this.options.mode != 'icon') this.el.addClass('mooeditable-ui-button-' + this.options.mode);
		
		this.active = false;
		this.disabled = false;

		// add hover effect for IE
		if (Browser.Engine.trident) this.el.addEvents({
			mouseenter: function(e){ this.addClass('hover'); },
			mouseleave: function(e){ this.removeClass('hover'); }
		});
		
		return this;
	},
	
	click: function(e){
		e.preventDefault();
		if (this.disabled) return;
		this.action(e);
	},
	
	action: function(){
		this.fireEvent('action', [this].concat($A(arguments)));
	},
	
	enable: function(){
		if (this.active) this.el.removeClass('onActive');
		if (!this.disabled) return;
		this.disabled = false;
		this.el.removeClass('disabled').set({
			disabled: false,
			opacity: 1
		});
		return this;
	},
	
	disable: function(){
		if (this.disabled) return;
		this.disabled = true;
		this.el.addClass('disabled').set({
			disabled: true,
			opacity: 0.4
		});
		return this;
	},
	
	activate: function(){
		if (this.disabled) return;
		this.active = true;
		this.el.addClass('onActive');
		return this;
	},
	
	deactivate: function(){
		this.active = false;
		this.el.removeClass('onActive');
		return this;
	}
	
});

MooEditable.UI.Dialog = new Class({

	Implements: [Events, Options],

	options:{
		/*
		onOpen: $empty,
		onClose: $empty,
		*/
		'class': '',
		contentClass: ''
	},

	initialize: function(html, options){
		this.setOptions(options);
		this.html = html;
		
		var self = this;
		this.el = new Element('div', {
			'class': 'mooeditable-ui-dialog ' + self.options['class'],
			html: '<div class="dialog-content ' + self.options.contentClass + '">' + html + '</div>',
			styles: {
				'display': 'none'
			},
			events: {
				click: self.click.bind(self)
			}
		});
	},
	
	toElement: function(){
		return this.el;
	},
	
	click: function(){
		this.fireEvent('click', arguments);
		return this;
	},
	
	open: function(){
		this.el.setStyle('display', '');
		this.fireEvent('open', this);
		return this;
	},
	
	close: function(){
		this.el.setStyle('display', 'none');
		this.fireEvent('close', this);
		return this;
	}

});

MooEditable.UI.AlertDialog = function(alertText){
	if (!alertText) return;
	var html = alertText + ' <button class="dialog-ok-button">OK</button>';
	return new MooEditable.UI.Dialog(html, {
		'class': 'mooeditable-alert-dialog',
		onOpen: function(){
			var button = this.el.getElement('.dialog-ok-button');
			(function(){
				button.focus();
			}).delay(10);
		},
		onClick: function(e){
			e.preventDefault();
			if (e.target.tagName.toLowerCase() != 'button') return;
			if (document.id(e.target).hasClass('dialog-ok-button')) this.close();
		}
	});
};

MooEditable.UI.PromptDialog = function(questionText, answerText, fn){
	if (!questionText) return;
	var html = '<label class="dialog-label">' + questionText
		+ ' <input type="text" class="text dialog-input" value="' + answerText + '">'
		+ '</label> <button class="dialog-button dialog-ok-button">OK</button>'
		+ '<button class="dialog-button dialog-cancel-button">Cancel</button>';
	return new MooEditable.UI.Dialog(html, {
		'class': 'mooeditable-prompt-dialog',
		onOpen: function(){
			var input = this.el.getElement('.dialog-input');
			(function(){
				input.focus();
				input.select();
			}).delay(10);
		},
		onClick: function(e){
			e.preventDefault();
			if (e.target.tagName.toLowerCase() != 'button') return;
			var button = document.id(e.target);
			var input = this.el.getElement('.dialog-input');
			if (button.hasClass('dialog-cancel-button')){
				input.set('value', answerText);
				this.close();
			} else if (button.hasClass('dialog-ok-button')){
				var answer = input.get('value');
				input.set('value', answerText);
				this.close();
				if (fn) fn.attempt(answer, this);
			}
		}
	});
};

MooEditable.Actions = new Hash({

	bold: {
		title: 'Bold',
		options: {
			shortcut: 'b'
		},
		states: {
			tags: ['b', 'strong'],
			css: {'font-weight': 'bold'}
		},
		events: {
			beforeToggleView: function(){
				if(Browser.Engine.gecko){
					var s = this.textarea.get('value')
					.replace(/<strong([^>]*)>/gi, '<b$1>')
					.replace(/<\/strong>/gi, '</b>')
					this.textarea.set('value',s);
				}
			},
			attach: function(){
				if(Browser.Engine.gecko){
					var s = this.textarea.get('value')
					.replace(/<strong([^>]*)>/gi, '<b$1>')
					.replace(/<\/strong>/gi, '</b>')
					this.textarea.set('value',s);
					this.setContent(s);
				}
			}
		}
	},
	
	italic: {
		title: 'Italic',
		options: {
			shortcut: 'i'
		},
		states: {
			tags: ['i', 'em'],
			css: {'font-style': 'italic'}
		},
		events: {
			beforeToggleView: function(){
				if (Browser.Engine.gecko){
					var s = this.textarea.get('value')
						.replace(/<embed([^>]*)>/gi, '<tmpembed$1>')
						.replace(/<em([^>]*)>/gi, '<i$1>')
						.replace(/<tmpembed([^>]*)>/gi, '<embed$1>')
						.replace(/<\/em>/gi, '</i>');
					this.textarea.set('value', s);
				}
			},
			attach: function(){
				if (Browser.Engine.gecko){
					var s = this.textarea.get('value')
						.replace(/<embed([^>]*)>/gi, '<tmpembed$1>')
						.replace(/<em([^>]*)>/gi, '<i$1>')
						.replace(/<tmpembed([^>]*)>/gi, '<embed$1>')
						.replace(/<\/em>/gi, '</i>');
					this.textarea.set('value', s);
					this.setContent(s);
				}
			}
		}
	},
	
	underline: {
		title: 'Underline',
		options: {
			shortcut: 'u'
		},
		states: {
			tags: ['u'],
			css: {'text-decoration': 'underline'}
		}
	},
	
	strikethrough: {
		title: 'Strikethrough',
		options: {
			shortcut: 's'
		},
		states: {
			tags: ['s', 'strike'],
			css: {'text-decoration': 'line-through'}
		}
	},
	
	insertunorderedlist: {
		title: 'Unordered List',
		states: {
			tags: ['ul']
		}
	},
	
	insertorderedlist: {
		title: 'Ordered List',
		states: {
			tags: ['ol']
		}
	},
	
	indent: {
		title: 'Indent',
		states: {
			tags: ['blockquote']
		}
	},
	
	outdent: {
		title: 'Outdent'
	},
	
	undo: {
		title: 'Undo',
		options: {
			shortcut: 'z'
		}
	},
	
	redo: {
		title: 'Redo',
		options: {
			shortcut: 'y'
		}
	},
	
	unlink: {
		title: 'Remove Hyperlink'
	},

	createlink: {
		title: 'Add Hyperlink',
		options: {
			shortcut: 'l'
		},
		states: {
			tags: ['a']
		},
		dialogs: {
			alert: MooEditable.UI.AlertDialog.pass('Please select the text you wish to hyperlink.'),
			prompt: function(editor){
				return MooEditable.UI.PromptDialog('Enter URL', 'http://', function(url){
					editor.execute('createlink', false, url.trim());
				});
			}
		},
		command: function(){
			if (this.selection.isCollapsed()){
				this.dialogs.createlink.alert.open();
			} else {
				var text = this.selection.getText();
				var prompt = this.dialogs.createlink.prompt;
				if (urlRegex.test(text)) prompt.el.getElement('.dialog-input').set('value', text);
				prompt.open();
			}
		}
	},

	urlimage: {
		title: 'Add Image',
		options: {
			shortcut: 'm'
		},
		dialogs: {
			prompt: function(editor){
				return MooEditable.UI.PromptDialog('Enter image URL', 'http://', function(url){
					editor.execute("insertimage", false, url.trim());
				});
			}
		},
		command: function(){
			this.dialogs.urlimage.prompt.open();
		}
	},

	toggleview: {
		title: 'Toggle View',
		command: function(){
			(this.mode == 'textarea') ? this.toolbar.enable() : this.toolbar.disable('toggleview');
			this.toggleView();
		}
	}

});

MooEditable.Actions.Settings = {};

Element.Properties.mooeditable = {

	set: function(options){
		return this.eliminate('mooeditable').store('mooeditable:options', options);
	},

	get: function(options){
		if (options || !this.retrieve('mooeditable')){
			if (options || !this.retrieve('mooeditable:options')) this.set('mooeditable', options);
			this.store('mooeditable', new MooEditable(this, this.retrieve('mooeditable:options')));
		}
		return this.retrieve('mooeditable');
	}

};

Element.implement({

	mooEditable: function(options){
		return this.get('mooeditable', options);
	}

});

})();
/*
---

script: MooEditable.Charmap.js

description: Extends MooEditable with a characters map

license: MIT-style license

authors:
- Ryan Mitchell

requires:
- /MooEditable
- /MooEditable.UI
- /MooEditable.Actions

usage:
	Add the following tags in your html
	<link rel="stylesheet" href="MooEditable.css">
	<link rel="stylesheet" href="MooEditable.Charmap.css">
	<script src="mootools.js"></script>
	<script src="MooEditable.js"></script>
	<script src="MooEditable.Charmap.js"></script>

	<script>
	window.addEvent('domready', function(){
		var mooeditable = $('textarea-1').mooEditable({
			actions: 'bold italic underline strikethrough | charmap | toggleview',
			externalCSS: '../../Assets/MooEditable/Editable.css'
		});
	});
	</script>

...
*/

MooEditable.charmap=[
	['&nbsp;', '&#160;'],
	['&amp;', '&#38;'],
	['&quot;', '&#34;'],
	['&cent;', '&#162;'],
	['&euro;', '&#8364;'],
	['&pound;', '&#163;'],
	['&yen;', '&#165;'],
	['&copy;', '&#169;'],
	['&reg;', '&#174;'],
	['&trade;', '&#8482;'],
	['&permil;', '&#8240;'],
	['&micro;', '&#181;'],
	['&middot;', '&#183;'],
	['&bull;', '&#8226;'],
	['&hellip;', '&#8230;'],
	['&prime;', '&#8242;'],
	['&Prime;', '&#8243;'],
	['&sect;', '&#167;'],
	['&para;', '&#182;'],
	['&szlig;', '&#223;'],
	['&lsaquo;', '&#8249;'],
	['&rsaquo;', '&#8250;'],
	['&laquo;', '&#171;'],
	['&raquo;', '&#187;'],
	['&lsquo;', '&#8216;'],
	['&rsquo;', '&#8217;'],
	['&ldquo;', '&#8220;'],
	['&rdquo;', '&#8221;'],
	['&sbquo;', '&#8218;'],
	['&bdquo;', '&#8222;'],
	['&lt;', '&#60;'],
	['&gt;', '&#62;'],
	['&le;', '&#8804;'],
	['&ge;', '&#8805;'],
	['&ndash;', '&#8211;'],
	['&mdash;', '&#8212;'],
	['&macr;', '&#175;'],
	['&oline;', '&#8254;'],
	['&curren;', '&#164;'],
	['&brvbar;', '&#166;'],
	['&uml;', '&#168;'],
	['&iexcl;', '&#161;'],
	['&iquest;', '&#191;'],
	['&circ;', '&#710;'],
	['&tilde;', '&#732;'],
	['&deg;', '&#176;'],
	['&minus;', '&#8722;'],
	['&plusmn;', '&#177;'],
	['&divide;', '&#247;'],
	['&frasl;', '&#8260;'],
	['&times;', '&#215;'],
	['&sup1;', '&#185;'],
	['&sup2;', '&#178;'],
	['&sup3;', '&#179;'],
	['&frac14;', '&#188;'],
	['&frac12;', '&#189;'],
	['&frac34;', '&#190;'],
	['&fnof;', '&#402;'],
	['&int;', '&#8747;'],
	['&sum;', '&#8721;'],
	['&infin;', '&#8734;'],
	['&radic;', '&#8730;'],
	['&sim;', '&#8764;'],
	['&cong;', '&#8773;'],
	['&asymp;', '&#8776;'],
	['&ne;', '&#8800;'],
	['&equiv;', '&#8801;'],
	['&isin;', '&#8712;'],
	['&notin;', '&#8713;'],
	['&ni;', '&#8715;'],
	['&prod;', '&#8719;'],
	['&and;', '&#8743;'],
	['&or;', '&#8744;'],
	['&not;', '&#172;'],
	['&cap;', '&#8745;'],
	['&cup;', '&#8746;'],
	['&part;', '&#8706;'],
	['&forall;', '&#8704;'],
	['&exist;', '&#8707;'],
	['&empty;', '&#8709;'],
	['&nabla;', '&#8711;'],
	['&lowast;', '&#8727;'],
	['&prop;', '&#8733;'],
	['&ang;', '&#8736;'],
	['&acute;', '&#180;'],
	['&cedil;', '&#184;'],
	['&ordf;', '&#170;'],
	['&ordm;', '&#186;'],
	['&dagger;', '&#8224;'],
	['&Dagger;', '&#8225;'],
	['&Agrave;', '&#192;'],
	['&Aacute;', '&#193;'],
	['&Acirc;', '&#194;'],
	['&Atilde;', '&#195;'],
	['&Auml;', '&#196;'],
	['&Aring;', '&#197;'],
	['&AElig;', '&#198;'],
	['&Ccedil;', '&#199;'],
	['&Egrave;', '&#200;'],
	['&Eacute;', '&#201;'],
	['&Ecirc;', '&#202;'],
	['&Euml;', '&#203;'],
	['&Igrave;', '&#204;'],
	['&Iacute;', '&#205;'],
	['&Icirc;', '&#206;'],
	['&Iuml;', '&#207;'],
	['&ETH;', '&#208;'],
	['&Ntilde;', '&#209;'],
	['&Ograve;', '&#210;'],
	['&Oacute;', '&#211;'],
	['&Ocirc;', '&#212;'],
	['&Otilde;', '&#213;'],
	['&Ouml;', '&#214;'],
	['&Oslash;', '&#216;'],
	['&OElig;', '&#338;'],
	['&Scaron;', '&#352;'],
	['&Ugrave;', '&#217;'],
	['&Uacute;', '&#218;'],
	['&Ucirc;', '&#219;'],
	['&Uuml;', '&#220;'],
	['&Yacute;', '&#221;'],
	['&Yuml;', '&#376;'],
	['&THORN;', '&#222;'],
	['&agrave;', '&#224;'],
	['&aacute;', '&#225;'],
	['&acirc;', '&#226;'],
	['&atilde;', '&#227;'],
	['&auml;', '&#228;'],
	['&aring;', '&#229;'],
	['&aelig;', '&#230;'],
	['&ccedil;', '&#231;'],
	['&egrave;', '&#232;'],
	['&eacute;', '&#233;'],
	['&ecirc;', '&#234;'],
	['&euml;', '&#235;'],
	['&igrave;', '&#236;'],
	['&iacute;', '&#237;'],
	['&icirc;', '&#238;'],
	['&iuml;', '&#239;'],
	['&eth;', '&#240;'],
	['&ntilde;', '&#241;'],
	['&ograve;', '&#242;'],
	['&oacute;', '&#243;'],
	['&ocirc;', '&#244;'],
	['&otilde;', '&#245;'],
	['&ouml;', '&#246;'],
	['&oslash;', '&#248;'],
	['&oelig;', '&#339;'],
	['&scaron;', '&#353;'],
	['&ugrave;', '&#249;'],
	['&uacute;', '&#250;'],
	['&ucirc;', '&#251;'],
	['&uuml;', '&#252;'],
	['&yacute;', '&#253;'],
	['&thorn;', '&#254;'],
	['&yuml;', '&#255;'],
	['&Alpha;', '&#913;'],
	['&Beta;', '&#914;'],
	['&Gamma;', '&#915;'],
	['&Delta;', '&#916;'],
	['&Epsilon;', '&#917;'],
	['&Zeta;', '&#918;'],
	['&Eta;', '&#919;'],
	['&Theta;', '&#920;'],
	['&Iota;', '&#921;'],
	['&Kappa;', '&#922;'],
	['&Lambda;', '&#923;'],
	['&Mu;', '&#924;'],
	['&Nu;', '&#925;'],
	['&Xi;', '&#926;'],
	['&Omicron;', '&#927;'],
	['&Pi;', '&#928;'],
	['&Rho;', '&#929;'],
	['&Sigma;', '&#931;'],
	['&Tau;', '&#932;'],
	['&Upsilon;', '&#933;'],
	['&Phi;', '&#934;'],
	['&Chi;', '&#935;'],
	['&Psi;', '&#936;'],
	['&Omega;', '&#937;'],
	['&alpha;', '&#945;'],
	['&beta;', '&#946;'],
	['&gamma;', '&#947;'],
	['&delta;', '&#948;'],
	['&epsilon;', '&#949;'],
	['&zeta;', '&#950;'],
	['&eta;', '&#951;'],
	['&theta;', '&#952;'],
	['&iota;', '&#953;'],
	['&kappa;', '&#954;'],
	['&lambda;', '&#955;'],
	['&mu;', '&#956;'],
	['&nu;', '&#957;'],
	['&xi;', '&#958;'],
	['&omicron;', '&#959;'],
	['&pi;', '&#960;'],
	['&rho;', '&#961;'],
	['&sigmaf;', '&#962;'],
	['&sigma;', '&#963;'],
	['&tau;', '&#964;'],
	['&upsilon;', '&#965;'],
	['&phi;', '&#966;'],
	['&chi;', '&#967;'],
	['&psi;', '&#968;'],
	['&omega;', '&#969;'],
	['&alefsym;', '&#8501;'],
	['&piv;', '&#982;'],
	['&real;', '&#8476;'],
	['&thetasym;', '&#977;'],
	['&upsih;', '&#978;'],
	['&weierp;', '&#8472;'],
	['&image;', '&#8465;'],
	['&larr;', '&#8592;'],
	['&uarr;', '&#8593;'],
	['&rarr;', '&#8594;'],
	['&darr;', '&#8595;'],
	['&harr;', '&#8596;'],
	['&crarr;', '&#8629;'],
	['&lArr;', '&#8656;'],
	['&uArr;', '&#8657;'],
	['&rArr;', '&#8658;'],
	['&dArr;', '&#8659;'],
	['&hArr;', '&#8660;'],
	['&there4;', '&#8756;'],
	['&sub;', '&#8834;'],
	['&sup;', '&#8835;'],
	['&nsub;', '&#8836;'],
	['&sube;', '&#8838;'],
	['&supe;', '&#8839;'],
	['&oplus;', '&#8853;'],
	['&otimes;', '&#8855;'],
	['&perp;', '&#8869;'],
	['&sdot;', '&#8901;'],
	['&lceil;', '&#8968;'],
	['&rceil;', '&#8969;'],
	['&lfloor;', '&#8970;'],
	['&rfloor;', '&#8971;'],
	['&lang;', '&#9001;'],
	['&rang;', '&#9002;'],
	['&loz;', '&#9674;'],
	['&spades;', '&#9824;'],
	['&clubs;', '&#9827;'],
	['&hearts;', '&#9829;'],
	['&diams;', '&#9830;']
];

MooEditable.UI.CharacterDialog = function(editor){
	var html = 'character <select class="char">';
	for (var i=0, len=MooEditable.charmap.length; i<len; i++) {
		html += '<option data-code="' + MooEditable.charmap[i][0] + '">' + MooEditable.charmap[i][1] + '</option>';
	}
	html += '</select>'
		+ '<button class="dialog-button dialog-ok-button">OK</button>'
		+ '<button class="dialog-button dialog-cancel-button">Cancel</button>';
	return new MooEditable.UI.Dialog(html, {
		'class': 'mooeditable-prompt-dialog',
		onClick: function(e){
			if (e.target.tagName.toLowerCase() == 'button') e.preventDefault();
			var button = document.id(e.target);
			if (button.hasClass('dialog-cancel-button')){
				this.close();
			} else if (button.hasClass('dialog-ok-button')){
				this.close();
				var sel = button.getPrevious('select.char');
				var div = new Element('div').set('html', sel.options[sel.selectedIndex].getProperty('data-code').trim());
				editor.selection.insertContent(div.get('html'));
			}
		}
	});
};

MooEditable.Actions.extend({
	
	charmap: {
		title: 'Insert custom character',
		dialogs: {
			prompt: function(editor){
				return MooEditable.UI.CharacterDialog(editor);
			}
		},
		command: function() {
			this.dialogs.charmap.prompt.open();
		},
		events: {
			toggleView: function(){
				if (this.mode == 'textarea'){
					var s = this.textarea.get('value');
					// when switching from iframe to textarea, we need to convert special symbols to html entities
					MooEditable.charmap.each(function(e){
						if (!['&amp;', '&gt;', '&lt;', '&quot;', '&nbsp;'].contains(e[0])){
							var r = new RegExp(String.fromCharCode(parseInt(e[1].replace('&#', '').replace(';', ''))), 'g');
							s = s.replace(r, e[0]);
						}
					}, this);
					this.textarea.set('value', s);
				}
			}
		}
	}
	
});
 
/*
---

script: MooEditable.Extras.js

description: Extends MooEditable to include more (simple) toolbar buttons.

license: MIT-style license

authors:
- Lim Chee Aun
- Ryan Mitchell

requires:
- /MooEditable
- /MooEditable.UI
- /MooEditable.UI.MenuList

...
*/

MooEditable.Actions.extend({

	formatBlock: {
		title: 'Block Formatting',
		type: 'menu-list',
		options: {
			list: [
				{text: 'Paragraph', value: 'p'},
				{text: 'Heading 1', value: 'h1', style: 'font-size:24px; font-weight:bold;'},
				{text: 'Heading 2', value: 'h2', style: 'font-size:18px; font-weight:bold;'},
				{text: 'Heading 3', value: 'h3', style: 'font-size:14px; font-weight:bold;'}
			]
		},
		states: {
			tags: ['p', 'h1', 'h2', 'h3']
		},
		command: function(menulist, name){
			var argument = '<' + name + '>';
			this.focus();
			this.execute('formatBlock', false, argument);
		}
	},
	
	justifyleft:{
		title: 'Align Left',
		states: {
			css: {'text-align': 'left'}
		}
	},
	
	justifyright:{
		title: 'Align Right',
		states: {
			css: {'text-align': 'right'}
		}
	},
	
	justifycenter:{
		title: 'Align Center',
		states: {
			tags: ['center'],
			css: {'text-align': 'center'}
		}
	},
	
	justifyfull:{
		title: 'Align Justify',
		states: {
			css: {'text-align': 'justify'}
		}
	},
	
	removeformat: {
		title: 'Remove Formatting'
	},
	
	insertHorizontalRule: {
		title: 'Insert Horizontal Rule',
		states: {
			tags: ['hr']
		},
		command: function(){
			this.selection.insertContent('<hr>');
		}
	}

});
 
/*
---

script: MooEditable.Flash.js

description: Extends MooEditable to embed Flash.

license: MIT-style license

authors:
- Radovan Lozej

requires:
- /MooEditable
- /MooEditable.UI
- /MooEditable.Actions

usage:
	Add the following tags in your html
	<link rel="stylesheet" href="MooEditable.css">
	<link rel="stylesheet" href="MooEditable.Flash.css">
	<script src="mootools.js"></script>
	<script src="MooEditable.js"></script>
	<script src="MooEditable.Flash.js"></script>

	<script>
	window.addEvent('domready', function(){
		var mooeditable = $('textarea-1').mooEditable({
			actions: 'bold italic underline strikethrough | flash | toggleview',
			externalCSS: '../../Assets/MooEditable/Editable.css'
		});
	});
	</script>

...
*/

MooEditable.UI.FlashDialog = function(editor){
	var html = 'embed <textarea class="dialog-f" value="" rows="2" cols="40" /></textarea> '
		+ '<button class="dialog-button dialog-ok-button">OK</button> '
		+ '<button class="dialog-button dialog-cancel-button">Cancel</button>';
	return new MooEditable.UI.Dialog(html, {
		'class': 'mooeditable-prompt-dialog',
		onOpen: function(){
			var input = this.el.getElement('.dialog-f');
			(function(){
				input.focus();
				input.select();
			}).delay(10);
		},
		onClick: function(e){
			if (e.target.tagName.toLowerCase() == 'button') e.preventDefault();
			var button = document.id(e.target);
			if (button.hasClass('dialog-cancel-button')){
				this.close();
			} else if (button.hasClass('dialog-ok-button')){
				this.close();
				var div = new Element('div').set('html', this.el.getElement('.dialog-f').get('value').trim());
				editor.selection.insertContent(div.get('html'));
			}
		}
	});
};

MooEditable.Actions.extend({
	
	flash: {
		title: 'Flash embed',
		dialogs: {
			prompt: function(editor){
				return MooEditable.UI.FlashDialog(editor);
			}
		},
		command: function(){
			this.dialogs.flash.prompt.open();
		}
	}
	
});
 
/*
---

script: MooEditable.Forecolor.js

description: Extends MooEditable to change the color of the text from a list a predefined colors.

license: MIT-style license

authors:
- Olivier Refalo

requires:
- /MooEditable
- /MooEditable.UI
- /MooEditable.UI.ButtonOverlay
- /MooEditable.Actions

usage:
	Add the following tags in your html
	<link rel="stylesheet" href="MooEditable.css">
	<link rel="stylesheet" href="MooEditable.Forecolor.css">
	<script src="mootools.js"></script>
	<script src="MooEditable.js"></script>
	<script src="MooEditable.UI.ButtonOverlay.js"></script>
	<script src="MooEditable.Forecolor.js"></script>

	<script>
	window.addEvent('domready', function(){
		var mooeditable = $('textarea-1').mooEditable({
			actions: 'bold italic underline strikethrough | forecolor | toggleview'
		});
	});
	</script>

...
*/

MooEditable.Actions.Settings.forecolor = {
	colors: [
		['000000', '993300', '333300', '003300', '003366', '000077', '333399', '333333'],
		['770000', 'ff6600', '777700', '007700', '007777', '0000ff', '666699', '777777'],
		['ff0000', 'ff9900', '99cc00', '339966', '33cccc', '3366f0', '770077', '999999'],
		['ff00ff', 'ffcc00', 'ffff00', '00ff00', '00ffff', '00ccff', '993366', 'cccccc'],
		['ff99cc', 'ffcc99', 'ffff99', 'ccffcc', 'ccffff', '99ccff', 'cc9977', 'ffffff']
	]
};

MooEditable.Actions.forecolor = {
	type: 'button-overlay',
	title: 'Change Color',
	options: {
		overlaySize: {x: 'auto'},
		overlayHTML: (function(){
			var html = '';
			MooEditable.Actions.Settings.forecolor.colors.each(function(row){
				row.each(function(c){
					html += '<a href="#" class="forecolor-colorpicker-color" style="background-color: #' + c + '" title="#' + c.toUpperCase() + '"></a>'; 
				});
				html += '<span class="forecolor-colorpicker-br"></span>';
			});
			return html;
		})()
	},
	command: function(buttonOverlay, e){
		var el = e.target;
		if (el.tagName.toLowerCase() != 'a') return;
		var color = $(el).getStyle('background-color');
		this.execute('forecolor', false, color);
		this.focus();
	}
};

 
/*
---

script: MooEditable.Group.js

description: Extends MooEditable to have multiple instances on a page controlled by one toolbar.

license: MIT-style license

authors:
- Ryan Mitchell

requires:
- core:1.2.4/Options
- /MooEditable
- /MooEditable.UI
- /MooEditable.Actions

provides: [MooEditable.Group]

...
*/

MooEditable.Group = new Class({

	Implements: [Options],
	
	options: {
		actions: 'bold italic underline strikethrough | insertunorderedlist insertorderedlist indent outdent | undo redo | createlink unlink | urlimage | toggleview'
	},
    
	initialize: function(toolbarEl, options){
		this.setOptions(options);
		this.actions = this.options.actions.clean().split(' ');
		var self = this;
		this.toolbar = new MooEditable.UI.Toolbar({
			onItemAction: function(){
				var args = $splat(arguments);
				var item = args[0];
				if (!self.activeEditor) return;
				self.activeEditor.focus();
				self.activeEditor.action(item.name, args);
				if (self.activeEditor.mode == 'iframe') self.activeEditor.checkStates();
			}
		}).render(this.actions);
		document.id(toolbarEl).adopt(this.toolbar);
	},

	add: function(textarea, options){
		return this.activeEditor = new MooEditable.Group.Item(textarea, this, $merge({toolbar: false}, this.options, options));
	}
	
});


MooEditable.Group.Item = new Class({

	Extends: MooEditable,

	initialize: function(textarea, group, options){
		this.group = group;
		this.parent(textarea, options);
		var focus = function(){
			this.group.activeEditor = this;
		}.bind(this);
		this.textarea.addEvent('focus', focus);
		this.win.addEvent('focus', focus);
	}

}); 
/*
---

script: MooEditable.Image.js

description: Extends MooEditable to insert image with manipulation options.

license: MIT-style license

authors:
- Radovan Lozej

requires:
- /MooEditable
- /MooEditable.UI
- /MooEditable.Actions

usage:
	Add the following tags in your html
	<link rel="stylesheet" href="MooEditable.css">
	<link rel="stylesheet" href="MooEditable.Image.css">
	<script src="mootools.js"></script>
	<script src="MooEditable.js"></script>
	<script src="MooEditable.Image.js"></script>

	<script>
	window.addEvent('domready', function(){
		var mooeditable = $('textarea-1').mooEditable({
			actions: 'bold italic underline strikethrough | image | toggleview'
		});
	});
	</script>

...
*/

MooEditable.UI.ImageDialog = function(editor){
	var html = 'url <input type="text" class="dialog-url" value="" size="15" /> '
		+ 'alt <input type="text" class="dialog-alt" value="" size="8" /> '
		+ 'class <input type="text" class="dialog-class" value="" size="8" /> '
		+ 'align <select class="dialog-align"><option>none</option><option>left</option><option>center</option><option>right</option></select> '
		+ '<button class="dialog-button dialog-ok-button">OK</button> '
		+ '<button class="dialog-button dialog-cancel-button">Cancel</button>';
		
	return new MooEditable.UI.Dialog(html, {
		'class': 'mooeditable-prompt-dialog',
		onOpen: function(){
			var input = this.el.getElement('.dialog-url');
			var node = editor.selection.getNode();
			if (node.get('tag') == 'img'){
				this.el.getElement('.dialog-url').set('value', node.get('src'));
				this.el.getElement('.dialog-alt').set('value', node.get('alt'));
				this.el.getElement('.dialog-class').set('value', node.className);
				this.el.getElement('.dialog-align').set('align', node.get('align'));
			}
			(function(){
				input.focus();
				input.select();
			}).delay(10);
		},
		onClick: function(e){
			if (e.target.tagName.toLowerCase() == 'button') e.preventDefault();
			var button = document.id(e.target);
			if (button.hasClass('dialog-cancel-button')){
				this.close();
			} else if (button.hasClass('dialog-ok-button')){
				this.close();
				var node = editor.selection.getNode();
				if (node.get('tag') == 'img'){
					node.set('src', this.el.getElement('.dialog-url').get('value').trim());
					node.set('alt', this.el.getElement('.dialog-alt').get('value').trim());
					node.className = this.el.getElement('.dialog-class').get('value').trim();
					node.set('align', this.el.getElement('.dialog-align').get('value'));
				} else {
					var div = new Element('div');
					new Element('img', {
						'src' : this.el.getElement('.dialog-url').get('value').trim(),
						'alt' : this.el.getElement('.dialog-alt').get('value').trim(),
						'class' : this.el.getElement('.dialog-class').get('value').trim(),
						'align' : this.el.getElement('.dialog-align').get('value')
					}).inject(div);
					editor.selection.insertContent(div.get('html'));
				}
			}
		}
	});
};

MooEditable.Actions.extend({
	
	image: {
		title: 'Add/Edit Image',
		options: {
			shortcut: 'm'
		},
		dialogs: {
			prompt: function(editor){
				return MooEditable.UI.ImageDialog(editor);
			}
		},
		command: function(){
			this.dialogs.image.prompt.open();
		}
	}
	
});
 
/*
---

script: MooEditable.Pagebreak.js

description: Extends MooEditable with pagebreak plugin

license: MIT-style license

authors:
- Ryan Mitchell

requires:
- /MooEditable
- /MooEditable.UI
- /MooEditable.Actions

usage:
	Add the following tags in your html
	<link rel="stylesheet" href="MooEditable.css">
	<link rel="stylesheet" href="MooEditable.Pagebreak.css">
	<script src="mootools.js"></script>
	<script src="MooEditable.js"></script>
	<script src="MooEditable.Pagebreak.js"></script>

	<script>
	window.addEvent('domready', function(){
		var mooeditable = $('textarea-1').mooEditable({
			actions: 'bold italic underline strikethrough | pagebreak | toggleview',
			externalCSS: '../../Assets/MooEditable/Editable.css'
		});
	});
	</script>

...
*/

MooEditable.Actions.Settings.pagebreak = {
	imageFile: '../../Assets/MooEditable/Other/pagebreak.gif'
};

MooEditable.Actions.extend({
	
	pagebreak: {
		title: 'Page break',
		command: function(){
			this.selection.insertContent('<img class="mooeditable-visual-aid mooeditable-pagebreak" />');
		},
		events: {
			beforeToggleView: function(){ // code to run when switching from iframe to textarea
				if (this.mode == 'iframe'){
					var s = this.getContent().replace(/<img([^>]*)class="mooeditable-visual-aid mooeditable-pagebreak"([^>]*)>/gi, '<!-- page break -->');
					this.setContent(s);
				} else {
					var s = this.textarea.get('value').replace(/<!-- page break -->/gi, '<img class="mooeditable-visual-aid mooeditable-pagebreak" />');
					this.textarea.set('value', s);
				}
			},
			render: function(){
				this.options.extraCSS = 'img.mooeditable-pagebreak { display:block; width:100%; height:16px; background: url('
					+ MooEditable.Actions.Settings.pagebreak.imageFile + ') repeat-x; }'
					+ this.options.extraCSS;
			}
		}
	}
		
});
 
/*
---

script: MooEditable.Smiley.js

description: Extends MooEditable to insert smiley/emoticons.

license: MIT-style license

authors:
- Olivier Refalo

requires:
- /MooEditable
- /MooEditable.UI
- /MooEditable.UI.ButtonOverlay
- /MooEditable.Actions

usage:
	Add the following tags in your html
	<link rel="stylesheet" href="MooEditable.css">
	<link rel="stylesheet" href="MooEditable.Smiley.css">
	<script src="mootools.js"></script>
	<script src="MooEditable.js"></script>
	<script src="MooEditable.UI.ButtonOverlay.js"></script>
	<script src="MooEditable.Smiley.js"></script>

	<script>
	window.addEvent('domready', function(){
		var mooeditable = $('textarea-1').mooEditable({
			actions: 'bold italic underline strikethrough | smiley | toggleview'
		});
	});
	</script>

...
*/

MooEditable.Actions.Settings.smiley = {
	imagesPath: '../../Assets/MooEditable/Smiley/',
	smileys: ['angryface', 'blush', 'gasp', 'grin', 'halo', 'lipsaresealed', 'smile', 'undecided', 'wink'],
	fileExt: '.png'
};

MooEditable.Actions.smiley = {
	type: 'button-overlay',
	title: 'Insert Smiley',
	options: {
		overlaySize: {x: 'auto'},
		overlayHTML: (function(){
			var settings = MooEditable.Actions.Settings.smiley;
			var html = '';
			settings.smileys.each(function(s){
				html += '<img src="'+ settings.imagesPath + s + settings.fileExt + '" alt="" class="smiley-image">'; 
			});
			return html;
		})()
	},
	command: function(buttonOverlay, e){
		var el = e.target;
		if (el.tagName.toLowerCase() != 'img') return;
		var src = $(el).get('src');
		var content = '<img style="border:0;" class="smiley" src="' + src + '" alt="">';
		this.focus();
		this.selection.insertContent(content);
	},
	events: {
		attach: function(editor){
			if (Browser.Engine.trident){
				// addListener instead of addEvent, because controlselect is a native event in IE
				editor.doc.addListener('controlselect', function(e){
					var el = e.target;
					if (el.tagName.toLowerCase() != 'img') return;
					if (!$(el).hasClass('smiley')) return;
					e.preventDefault();
				});
			}
		},
		editorMouseDown: function(e, editor){
			var el = e.target;
			var isSmiley = (el.tagName.toLowerCase() == 'img') && $(el).hasClass('smiley');
			$try(function(){
				editor.doc.execCommand('enableObjectResizing', false, !isSmiley);
			});
		}
	}
};
 
/*
---

script: MooEditable.Table.js

description: Extends MooEditable to insert table with manipulation options.

license: MIT-style license

authors:
- Radovan Lozej
- Ryan Mitchell

requires:
- /MooEditable
- /MooEditable.UI
- /MooEditable.Actions

usage:
	Add the following tags in your html
	<link rel="stylesheet" href="MooEditable.css">
	<link rel="stylesheet" href="MooEditable.Table.css">
	<script src="mootools.js"></script>
	<script src="MooEditable.js"></script>
	<script src="MooEditable.Table.js"></script>

	<script>
	window.addEvent('domready', function(){
		var mooeditable = $('textarea-1').mooEditable({
			actions: 'bold italic underline strikethrough | table | toggleview'
		});
	});
	</script>

...
*/

MooEditable.UI.TableDialog = function(editor, dialog){
	var html = {
		tableadd: 'columns <input type="text" class="table-c" value="" size="4" /> '
			+ 'rows <input type="text" class="table-r" value="" size="4" /> ',
		tableedit: 'width <input type="text" class="table-w" value="" size="4" /> '
			+ 'class <input type="text" class="table-c" value="" size="15" /> ',
		tablerowedit: 'class <input type="text" class="table-c" value="" size="15" /> type <select class="table-c-type"><option value="th">Header</option><option value="td">Cell</option></select> ',
		tablecoledit: 'width <input type="text" class="table-w" value="" size="4" /> '
			+ 'class <input type="text" class="table-c" value="" size="15" /> '
			+ 'align <select class="table-a"><option>none</option><option>left</option><option>center</option><option>right</option></select> '
			+ 'valign <select class="table-va"><option>none</option><option>top</option><option>middle</option><option>bottom</option></select> '
	};
	html[dialog] += '<button class="dialog-button dialog-ok-button">OK</button>'
		+ '<button class="dialog-button dialog-cancel-button">Cancel</button>';
		
	var action = {
		tableadd: {
			click: function(e){
				var col = this.el.getElement('.table-c').value.toInt();
				var row = this.el.getElement('.table-r').value.toInt();
				if (!(row>0 && col>0)) return;
				var div, table, tbody, ro = [];
				div = new Element('tdiv');
				table = new Element('table').set('border', 0).set('width', '100%').inject(div);
				tbody = new Element('tbody').inject(table);
				for (var r = 0;r<row;r++){
					ro[r] = new Element('tr').inject(tbody, 'bottom');
					for (var c=0; c<col; c++) new Element('td').set('html', '&nbsp;').inject(ro[r], 'bottom');
				}
				editor.selection.insertContent(div.get('html'));
			}
		},
		tableedit: {
			load: function(e){
				var node = editor.selection.getNode().getParent('table');
				this.el.getElement('.table-w').set('value', node.get('width'));
				this.el.getElement('.table-c').set('value', node.className);
			},
			click: function(e){
				var node = editor.selection.getNode().getParent('table');
				node.set('width', this.el.getElement('.table-w').value);
				node.className = this.el.getElement('.table-c').value;
			}
		},
		tablerowedit: {
			load: function(e){
				var node = editor.selection.getNode().getParent('tr');
				this.el.getElement('.table-c').set('value', node.className);
				this.el.getElement('.table-c-type').set('value', editor.selection.getNode().get('tag'));
			},
			click: function(e){
				var node = editor.selection.getNode().getParent('tr');
				node.className = this.el.getElement('.table-c').value;
				node.getElements('td,th').each(function(c){
					if (this.el.getElement('.table-c-type') != c.get('tag')){
						var n = editor.doc.createElement(this.el.getElement('.table-c-type').get('value'));
						$(n).set('html',c.get('html')).replaces(c);
					}
				},this);
			}
		},
		tablecoledit: {
			load : function(e){
				var node = editor.selection.getNode();
				if (node.get('tag') != 'td') node = node.getParent('td');
				this.el.getElement('.table-w').set('value', node.get('width'));
				this.el.getElement('.table-c').set('value', node.className);
				this.el.getElement('.table-a').set('value', node.get('align'));
				this.el.getElement('.table-va').set('value', node.get('valign'));
			},
			click: function(e){
				var node = editor.selection.getNode();
				if (node.get('tag') != 'td') node = node.getParent('td');
				node.set('width', this.el.getElement('.table-w').value);
				node.className = this.el.getElement('.table-c').value;
				node.set('align', this.el.getElement('.table-a').value);
				node.set('valign', this.el.getElement('.table-va').value);
			}
		}
	};
	
	return new MooEditable.UI.Dialog(html[dialog], {
		'class': 'mooeditable-prompt-dialog',
		onOpen: function(){
			if (action[dialog].load) action[dialog].load.apply(this);
			var input = this.el.getElement('input');
			(function(){ input.focus(); }).delay(10);
		},
		onClick: function(e){
			if (e.target.tagName.toLowerCase() == 'button') e.preventDefault();
			var button = document.id(e.target);
			if (button.hasClass('dialog-cancel-button')){
				this.close();
			} else if (button.hasClass('dialog-ok-button')){
				this.close();
				action[dialog].click.apply(this);
			}
		}
	});
};

MooEditable.Actions.extend({

	tableadd:{
		title: 'Add Table',
		dialogs: {
			prompt: function(editor){
				return MooEditable.UI.TableDialog(editor, 'tableadd');
			}
		},
		command: function(){
			this.dialogs.tableadd.prompt.open();
		}
	},
	
	tableedit:{
		title: 'Edit Table',
		dialogs: {
			prompt: function(editor){
				return MooEditable.UI.TableDialog(editor, 'tableedit');
			}
		},
		command: function(){
			if (this.selection.getNode().getParent('table')) this.dialogs.tableedit.prompt.open();
		}
	},
	
	tablerowadd:{
		title: 'Add Row',
		command: function(){
			var node = this.selection.getNode().getParent('tr');
			if (node) node.clone().inject(node, 'after');
		}
	},
	
	tablerowedit:{
		title: 'Edit Row',
		dialogs: {
			prompt: function(editor){
				return MooEditable.UI.TableDialog(editor, 'tablerowedit');
			}
		},
		command: function(){
			if (this.selection.getNode().getParent('table')) this.dialogs.tablerowedit.prompt.open();
		}
	},
	
	tablerowspan:{
		title: 'Merge Row',
		command: function(){
			var node = this.selection.getNode();
			if (node.get('tag') != 'td') node = node.getParent('td');
			if (node){
				var index = node.cellIndex;
				var row = node.getParent().rowIndex;
				if (node.getParent().getParent().childNodes[row+node.rowSpan]){
					node.getParent().getParent().childNodes[row+node.rowSpan].deleteCell(index);
					node.rowSpan++;
				}
			}
		}
	},
	
	tablerowsplit:{
		title: 'Split Row',
		command: function(){
			var node = this.selection.getNode();
			if (node.get('tag') != 'td') node = node.getParent('td');
			if (node){
				var index = node.cellIndex;
				var row = node.getParent().rowIndex;
				if (node.getProperty('rowspan')){
					var rows = parseInt(node.getProperty('rowspan'));
					for (i=1; i<rows; i++){
						node.getParent().getParent().childNodes[row+i].insertCell(index);
					}
					node.removeProperty('rowspan');
				}
			}
		},
		states: function(node){
			if (node.get('tag') != 'td') return;
			if (node){
				if (node.getProperty('rowspan') && parseInt(node.getProperty('rowspan')) > 1){
					this.el.addClass('onActive');
				}
			}
		}
	},
	
	tablerowdelete:{
		title: 'Delete Row',
		command: function(){
			var node = this.selection.getNode().getParent('tr');
			if (node) node.getParent().deleteRow(node.rowIndex);
		}
	},
	
	tablecoladd:{
		title: 'Add Column',
		command: function(){
			var node = this.selection.getNode();
			if (node.get('tag') != 'td') node = node.getParent('td');
			if (node){
				var index = node.cellIndex;
				var len = node.getParent().getParent().childNodes.length;
				for (var i=0; i<len; i++){
					var ref = $(node.getParent().getParent().childNodes[i].childNodes[index]);
					ref.clone().inject(ref, 'after');
				}
			}
		}
	},
	
	tablecoledit:{
		title: 'Edit Column',
		dialogs: {
			prompt: function(editor){
				return MooEditable.UI.TableDialog(editor, 'tablecoledit');
			}
		},
		command: function(){
			if (this.selection.getNode().getParent('table')) this.dialogs.tablecoledit.prompt.open();
		}
	},
	
	tablecolspan:{
		title: 'Merge Cell',
		command: function(){
			var node = this.selection.getNode();
			if (node.get('tag')!='td') node = node.getParent('td');
			if (node){
				var index = node.cellIndex + 1;
				if (node.getParent().childNodes[index]){
					node.getParent().deleteCell(index);
					node.colSpan++;
				}
			}
		}
	},
		
	tablecolsplit:{
		title: 'Split Cell',
		command: function(){
			var node = this.selection.getNode();
			if (node.get('tag')!='td') node = node.getParent('td');
			if (node){
				var index = node.cellIndex + 1;
				if(node.getProperty('colspan')){
					var cols = parseInt(node.getProperty('colspan'));
					for (i=1;i<cols;i++){
						node.getParent().insertCell(index+i);
					}
					node.removeProperty('colspan');
				}
			}
		},
		states: function(node){
			if (node.get('tag')!='td') return;
			if (node){
				if (node.getProperty('colspan') && parseInt(node.getProperty('colspan')) > 1){
					this.el.addClass('onActive');
				}
			}
		}
	},
	
	tablecoldelete:{
		title: 'Delete Column',
		command: function(){
			var node = this.selection.getNode();
			if (node.get('tag') != 'td') node = node.getParent('td');
			if (node){
				var len = node.getParent().getParent().childNodes.length;
				var index = node.cellIndex;
				var tt = node.getParent().getParent();
				for (var i=0; i<len; i++) tt.childNodes[i].deleteCell(index);
			}
		}
	}
	
});
 
/*
---

script: MooEditable.UI.ButtonOverlay.js

description: UI Class to create a button element with a popup overlay.

license: MIT-style license

authors:
- Lim Chee Aun

requires:
- /MooEditable
- /MooEditable.UI

provides: [MooEditable.UI.ButtonOverlay]

...
*/

MooEditable.UI.ButtonOverlay = new Class({

	Extends: MooEditable.UI.Button,

	options: {
		/*
		onOpenOverlay: $empty,
		onCloseOverlay: $empty,
		*/
		overlayHTML: '',
		overlayClass: '',
		overlaySize: {x: 150, y: 'auto'},
		overlayContentClass: ''
	},

	initialize: function(options){
		this.parent(options);
		this.render();
		this.el.addClass('mooeditable-ui-buttonOverlay');
		this.renderOverlay(this.options.overlayHTML);
	},
	
	renderOverlay: function(html){
		var self = this;
		this.overlay = new Element('div', {
			'class': 'mooeditable-ui-button-overlay ' + self.name + '-overlay ' + self.options.overlayClass,
			html: '<div class="overlay-content ' + self.options.overlayContentClass + '">' + html + '</div>',
			tabindex: 0,
			styles: {
				left: '-999em',
				position: 'absolute',
				width: self.options.overlaySize.x,
				height: self.options.overlaySize.y
			},
			events: {
				mousedown: self.clickOverlay.bind(self),
				focus: self.openOverlay.bind(self),
				blur: self.closeOverlay.bind(self)
			}
		}).inject(document.body).store('MooEditable.UI.ButtonOverlay', this);
		this.overlayVisible = false;
	},
	
	openOverlay: function(){
		if (this.overlayVisible) return;
		this.overlayVisible = true;
		this.activate();
		this.fireEvent('openOverlay', this);
		return this;
	},
	
	closeOverlay: function(){
		if (!this.overlayVisible) return;
		this.overlay.setStyle('left', '-999em');
		this.overlayVisible = false;
		this.deactivate();
		this.fireEvent('closeOverlay', this);
		return this;
	},
	
	clickOverlay: function(e){
		if (e.target == this.overlay || e.target.parentNode == this.overlay) return;
		this.overlay.blur();
		e.preventDefault();
		this.action(e);
	},
	
	click: function(e){
		e.preventDefault();
		if (this.disabled) return;
		if (this.overlayVisible){
			this.overlay.blur();
			return;
		} else {
			var coords = this.el.getCoordinates();
			this.overlay.setStyles({
				top: coords.bottom,
				left: coords.left
			});
			this.overlay.focus();
		}
	}
	
}); 
/*
---

script: MooEditable.UI.MenuList.js

description: UI Class to create a menu list (select) element.

license: MIT-style license

authors:
- Lim Chee Aun

requires:
- /MooEditable
- /MooEditable.UI

provides: [MooEditable.UI.MenuList]

...
*/

MooEditable.UI.MenuList = new Class({

	Implements: [Events, Options],

	options: {
		/*
		onAction: $empty,
		*/
		title: '',
		name: '',
		'class': '',
		list: []
	},

	initialize: function(options){
		this.setOptions(options);
		this.name = this.options.name;
		this.render();
	},
	
	toElement: function(){
		return this.el;
	},
	
	render: function(){
		var self = this;
		var html = '';
		this.options.list.each(function(item){
			html += '<option value="{value}" style="{style}">{text}</option>'.substitute(item);
		});
		this.el = new Element('select', {
			'class': self.options['class'],
			title: self.options.title,
			html: html,
			styles: { 'height' : '21px' },
			events: {
				change: self.change.bind(self)
			}
		});
		
		this.disabled = false;

		// add hover effect for IE
		if (Browser.Engine.trident) this.el.addEvents({
			mouseenter: function(e){ this.addClass('hover'); },
			mouseleave: function(e){ this.removeClass('hover'); }
		});
		
		return this;
	},
	
	change: function(e){
		e.preventDefault();
		if (this.disabled) return;
		var name = e.target.value;
		this.action(name);
	},
	
	action: function(){
		this.fireEvent('action', [this].concat($A(arguments)));
	},
	
	enable: function(){
		if (!this.disabled) return;
		this.disabled = false;
		this.el.set('disabled', false).removeClass('disabled').set({
			disabled: false,
			opacity: 1
		});
		return this;
	},
	
	disable: function(){
		if (this.disabled) return;
		this.disabled = true;
		this.el.set('disabled', true).addClass('disabled').set({
			disabled: true,
			opacity: 0.4
		});
		return this;
	},
	
	activate: function(value){
		if (this.disabled) return;
		var index = 0;
		if (value) this.options.list.each(function(item, i){
			if (item.value == value) index = i;
		});
		this.el.selectedIndex = index;
		return this;
	},
	
	deactivate: function(){
		this.el.selectedIndex = 0;
		this.el.removeClass('onActive');
		return this;
	}
	
});
 
 
