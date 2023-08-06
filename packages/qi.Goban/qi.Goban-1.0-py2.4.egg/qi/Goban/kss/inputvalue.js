
new function () {
kukit.actionsGlobalRegistry.register('setInputValue', function (oper) {
;;; oper.componentName = '[setInputValue] action';
	oper.evaluateParameters(['newValue']);
	var newValue = oper.parms.newValue;
	var node = oper.node;
	node.value = newValue;
});
kukit.commandsGlobalRegistry.registerFromAction(
    'setInputValue', kukit.cr.makeSelectorCommand);
}();
