package armory.trait.internal;

#if arm_physics
import haxebullet.Bullet;
#end
import iron.Trait;
import iron.math.Vec4;
import iron.object.Transform;
import iron.object.MeshObject;

@:keep
class RigidBody extends Trait {

#if (!arm_physics)
	public function new() { super(); }
#else

	var shape:Shape;
	var _motionState:BtMotionStatePointer;

	public var physics:PhysicsWorld;
	public var transform:Transform = null;

	public var mass:Float;
	public var friction:Float;
	public var collisionMargin:Float;
	public var linearDamping:Float;
	public var angularDamping:Float;
	public var passive:Bool;

	public var body:BtRigidBodyPointer = null;
	public var ready = false;
	public var shapeConvexCreated:Bool;

	static var nextId = 0;
	public var id = 0;

	public var onReady:Void->Void = null;

	public function new(mass = 1.0, shape = Shape.Box, friction = 0.5, collisionMargin = 0.0,
						linearDamping = 0.04, angularDamping = 0.1, passive = false) {
		super();

		this.mass = mass;
		this.shape = shape;
		this.friction = friction;
		this.collisionMargin = collisionMargin;
		this.linearDamping = linearDamping;
		this.angularDamping = angularDamping;
		this.passive = passive;
		
		Scene.active.notifyOnInit(function() {
			notifyOnInit(init);
			notifyOnLateUpdate(lateUpdate);
			notifyOnRemove(removeFromWorld);
		});
	}
	
	inline function withMargin(f:Float) {
		return f - f * collisionMargin;
	}

	public function notifyOnReady(f:Void->Void) {
		onReady = f;
	}

	public function init() {
		transform = object.transform;
		physics = armory.trait.internal.PhysicsWorld.active;

		if (ready) return;
		ready = true;

		var _shape:BtCollisionShapePointer = null;
		var _shapeConvex:BtConvexHullShapePointer = null;
		shapeConvexCreated = false;
		var _inertia = BtVector3.create(0, 0, 0);

		if (shape == Shape.Box) {
			_shape = BtBoxShape.create(BtVector3.create(
				withMargin(transform.size.x / 2),
				withMargin(transform.size.y / 2),
				withMargin(transform.size.z / 2)).value);
		}
		else if (shape == Shape.Sphere) {
			_shape = BtSphereShape.create(withMargin(transform.size.x / 2));
		}
		else if (shape == Shape.ConvexHull || shape == Shape.Mesh) { // Use convex hull for mesh for now
			_shapeConvex = BtConvexHullShape.create();
			shapeConvexCreated = true;
			addPointsToConvexHull(_shapeConvex, transform.scale, collisionMargin);
		}
		else if (shape == Shape.Cone) {
			_shape = BtConeShapeZ.create(
				withMargin(transform.size.x / 2), // Radius
				withMargin(transform.size.z));	  // Height
		}
		else if (shape == Shape.Cylinder) {
			_shape = BtCylinderShapeZ.create(BtVector3.create(
				withMargin(transform.size.x / 2),
				withMargin(transform.size.y / 2),
				withMargin(transform.size.z / 2)).value);
		}
		else if (shape == Shape.Capsule) {
			var r = transform.size.x / 2;
			_shape = BtCapsuleShapeZ.create(
				withMargin(r), // Radius
				withMargin(transform.size.z - r * 2)); // Height between 2 sphere centers
		}
		//else if (shape == SHAPE_TERRAIN) {
			// var data:Array<Dynamic> = [];
			// _shape = BtHeightfieldTerrainShape.create(3, 3, data, 1, -10, 10, 2, 0, true);
		//}
		else if (shape == Shape.StaticMesh || shape == Shape.Terrain) {
			var meshInterface = BtTriangleMesh.create(true, true);
			fillTriangleMesh(meshInterface, transform.scale);
			_shape = BtBvhTriangleMeshShape.create(meshInterface, true, true);
		}

		var _transform = BtTransform.create();
		_transform.value.setIdentity();
		_transform.value.setOrigin(BtVector3.create(
			transform.loc.x,
			transform.loc.y,
			transform.loc.z).value);
		_transform.value.setRotation(BtQuaternion.create(
			transform.rot.x,
			transform.rot.y,
			transform.rot.z,
			transform.rot.w).value);

		var _centerOfMassOffset = BtTransform.create();
		_centerOfMassOffset.value.setIdentity();
		_motionState = BtDefaultMotionState.create(_transform.value, _centerOfMassOffset.value);

		if (!shapeConvexCreated) {
			if (shape != Shape.StaticMesh && shape != Shape.Terrain) {
				_shape.ptr.calculateLocalInertia(mass, _inertia);
			}
			var _bodyCI = BtRigidBodyConstructionInfo.create(mass, _motionState, _shape, _inertia.value);
			body = BtRigidBody.create(_bodyCI.value);
			body.ptr.setFriction(friction);
			body.ptr.setRollingFriction(friction);
		}
		else {
			_shapeConvex.ptr.calculateLocalInertia(mass, _inertia);
			var _bodyCI = BtRigidBodyConstructionInfo.create(mass, _motionState, _shapeConvex, _inertia.value);
			body = BtRigidBody.create(_bodyCI.value);
		}

		id = nextId;
		nextId++;

		if (linearDamping != 0.04 || angularDamping != 0.1) {
			body.setDamping(linearDamping, angularDamping);
		}

		#if js
		//body.setUserIndex(nextId);
		untyped body.userIndex = id;
		#elseif cpp
		body.ptr.setUserIndex(id);
		#end

		physics.addRigidBody(this);

		if (onReady != null) onReady();
	}

	function lateUpdate() {
		if (!ready) return;
		if (object.animation != null || passive) {
			syncTransform();
		}
		else {
			var trans = body.ptr.getWorldTransform();
			var p = trans.getOrigin();
			var q = trans.getRotation();
			transform.loc.set(p.x(), p.y(), p.z());
			transform.rot.set(q.x(), q.y(), q.z(), q.w());
			transform.dirty = true;
			transform.update();
		}
	}

	public function removeFromWorld() {
		if (physics != null) physics.removeRigidBody(this);
	}

	public function activate() {
		body.ptr.activate(false);
	}

	public function disableGravity() {
		// TODO: use setGravity instead
		setLinearFactor(0, 0, 0);
		setAngularFactor(0, 0, 0);
	}

	/*public function setGravity(v:Vec4) {
		body.ptr.setGravity(BtVector3.create(v.x, v.y, v.z).value);
	}*/

	/*public function setActivationState(newState:Int) {
		body.ptr.setActivationState(newState);
	}*/

	public function applyImpulse(impulse:Vec4, loc:Vec4 = null) {
		if (loc == null) {
			body.ptr.applyCentralImpulse(BtVector3.create(impulse.x, impulse.y, impulse.z).value);
		}
		else {
			body.ptr.applyImpulse(BtVector3.create(impulse.x, impulse.y, impulse.z).value,
								  BtVector3.create(loc.x, loc.y, loc.z).value);
		}
	}

	public function setLinearFactor(x:Float, y:Float, z:Float) {
		body.ptr.setLinearFactor(BtVector3.create(x, y, z).value);
	}

	public function setAngularFactor(x:Float, y:Float, z:Float) {
		body.ptr.setAngularFactor(BtVector3.create(x, y, z).value);
	}

	public function getLinearVelocity():BtVector3 {
		return body.ptr.getLinearVelocity(); // Unable to compile in cpp
	}

	public function setLinearVelocity(x:Float, y:Float, z:Float) {
		body.ptr.setLinearVelocity(BtVector3.create(x, y, z).value);
	}

	// public function getAngularVelocity():BtVector3 {
	// 	return body.ptr.getAngularVelocity();
	// }

	public function setAngularVelocity(x:Float, y:Float, z:Float) {
		body.ptr.setAngularVelocity(BtVector3.create(x, y, z).value);
	}

	public function syncTransform() {
		var trans = BtTransform.create();
		trans.value.setOrigin(BtVector3.create(transform.loc.x, transform.loc.y, transform.loc.z).value);
		trans.value.setRotation(BtQuaternion.create(transform.rot.x, transform.rot.y, transform.rot.z, transform.rot.w).value);
		body.ptr.setCenterOfMassTransform(trans.value);
		// _motionState.getWorldTransform(trans);
		// trans.setOrigin(BtVector3.create(transform.loc.x, transform.loc.y, transform.loc.z).value);
		// _motionState.setWorldTransform(trans);
	}

	function addPointsToConvexHull(shape:BtConvexHullShapePointer, scale:Vec4, margin:Float) {
		var positions = cast(object, MeshObject).data.mesh.positions;

		var sx = scale.x * (1.0 - margin);
		var sy = scale.y * (1.0 - margin);
		var sz = scale.z * (1.0 - margin);

		for (i in 0...Std.int(positions.length / 3)) {
			#if js
			shape.addPoint(
			#elseif cpp
			shape.ptr.addPoint(
			#end
				BtVector3.create(positions[i * 3] * sx, positions[i * 3 + 1] * sy, positions[i * 3 + 2] * sz).value, true);
		}
	}

	function fillTriangleMesh(triangleMesh:BtTriangleMeshPointer, scale:Vec4) {
		var positions = cast(object, MeshObject).data.mesh.positions;
		var indices = cast(object, MeshObject).data.mesh.indices;

		for (i in 0...Std.int(indices[0].length / 3)) {
			triangleMesh.ptr.addTriangle(
				BtVector3.create(positions[indices[0][i * 3 + 0] * 3 + 0] * scale.x,
							  	 positions[indices[0][i * 3 + 0] * 3 + 1] * scale.y,
							  	 positions[indices[0][i * 3 + 0] * 3 + 2] * scale.z).value,
				BtVector3.create(positions[indices[0][i * 3 + 1] * 3 + 0] * scale.x,
							  	 positions[indices[0][i * 3 + 1] * 3 + 1] * scale.y,
							  	 positions[indices[0][i * 3 + 1] * 3 + 2] * scale.z).value,
				BtVector3.create(positions[indices[0][i * 3 + 2] * 3 + 0] * scale.x,
							  	 positions[indices[0][i * 3 + 2] * 3 + 1] * scale.y,
							  	 positions[indices[0][i * 3 + 2] * 3 + 2] * scale.z).value
			);
		}
	}
#end
}

@:enum abstract Shape(Int) from Int {
	var Box = 0;
	var Sphere = 1;
	var ConvexHull = 2;
	var Mesh = 3;
	var Cone = 4;
	var Cylinder = 5;
	var Capsule = 6;
	var Terrain = 7;
	var StaticMesh = 8;
}
