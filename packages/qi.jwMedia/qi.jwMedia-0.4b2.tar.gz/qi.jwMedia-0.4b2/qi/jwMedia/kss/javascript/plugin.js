new function () {
kukit.actionsGlobalRegistry.register('JWPlayer-enable', function (oper) {
;;; oper.componentName = '[JWPlayer-enable] action';
    
	oper.evaluateParameters(['file','type'], 
                            {'height':240,
							'width':320,
							'image':'',
							'logo':'',
							'stretching':'uniform',
							'allowfullscreen':false,
							'captions':''}
							);
	oper.evalInt('height');
	oper.evalInt('width');
    oper.evalBool('allowfullscreen');
    var node = oper.node;

    var swf = new SWFObject("/++resource++qi.jwMedia.resources/player.swf","player",oper.parms.width,oper.parms.height,"7");
	swf.addVariable("file",encodeURIComponent(oper.parms.file));
	swf.addVariable('type',oper.parms.type);

	swf.addVariable("height",oper.parms.height);
	swf.addVariable("width",oper.parms.width);
	if (oper.parms.allowfullscreen)
		swf.addVariable("fullscreen",'true');
	else 
		swf.addVariable("fullscreen",'false');
	swf.addParam("allowfullscreen",oper.parms.allowfullscreen);

	if (oper.parms.image!='')
		swf.addVariable("image",encodeURIComponent(oper.parms.image));
	if (oper.parms.logo)
		swf.addVariable("logo",encodeURIComponent(oper.parms.logo));
	swf.addVariable("stretching",oper.parms.stretching);

	if (oper.parms.captions!='') {
		swf.addVariable("plugins","captions-1");
		swf.addVariable("captions.file",oper.parms.captions);
		swf.addVariable('captions.state', 'false');
	}
	// Only for bought version
	//swf.addVariable("abouttext","About qi.jwMedia")
	//swf.addVariable("aboutlink","http://qiweb.net")

	swf.write(node);

});
kukit.commandsGlobalRegistry.registerFromAction(
    'JWPlayer-enable', kukit.cr.makeSelectorCommand);
}();
