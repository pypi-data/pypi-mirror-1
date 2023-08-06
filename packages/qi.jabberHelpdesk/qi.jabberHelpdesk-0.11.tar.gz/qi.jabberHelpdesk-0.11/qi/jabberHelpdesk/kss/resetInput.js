
new function () {
kukit.actionsGlobalRegistry.register('resetInput', function (oper) {
;;; oper.componentName = '[resetInput] action';
    
	var node = oper.node;
	node.value = '';
});
kukit.commandsGlobalRegistry.registerFromAction(
    'resetInput', kukit.cr.makeSelectorCommand);
}();
