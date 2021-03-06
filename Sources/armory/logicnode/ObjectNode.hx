package armory.logicnode;

import armory.trait.internal.NodeExecutor;

class ObjectNode extends Node {

	public var target:iron.object.Object;
	public var property0:String;

	public function new() {
		super();
	}

	public override function start(executor:NodeExecutor, parent:Node = null) {
		super.start(executor, parent);
		executor.notifyOnNodeInit(init);
	}

	function init() {
		target = armory.Scene.active.getChild(property0);
		inputChanged();
	}

	public static function create(_property0:String):ObjectNode {
		var n = new ObjectNode();
		n.property0 = _property0;
		return n;
	}
}
