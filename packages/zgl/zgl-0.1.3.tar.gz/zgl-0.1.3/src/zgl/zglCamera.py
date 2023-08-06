from OpenGL.GL import *
from OpenGL.GLU import *
from zglUtils import *

class zglCamera:
	def __init__(self):
		# Camera variables
		self.position = [0.0, 0.0, -1.0]
		self.lookat = [0.0, 0.0, 0.0]
		self.up = [0.0, 1.0, 0.0]
		
#	def setPosition(self, *args):
#		self.position		

	def setView(self):
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		gluLookAt(	self.position[0], self.position[1], self.position[2],	# Camera position
					self.lookat[0], self.lookat[1], self.lookat[2],	# Camera look at
					self.up[0], self.up[1], self.up[2] )	# Up vector


class zglPerspective:
	def __init__(self):
		self.fov = 45.0
		self.width = 640.0
		self.height = 480.0
		self.near = 1.0
		self.far = 100.0
		
	def setProjection(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(self.fov, 1.0*self.width/self.height, self.near, self.far)



# A class that defines an infinite plane, given by the equation
# 		ax + by + cz + d = 0
#
class zglPlane:
	def __init__(self, a, b, c, d):
		self.a = a
		self.b = b
		self.c = c
		self.d = d
		
	@staticmethod
	def fromNormalAndPoint(normal, point):
		# normal and point are both assumed to be 3-element lists
		d = -sum( zglVector.multiply(normal, point) )
		
		return zglPlane(normal[0], normal[1], normal[2], d)
		
	# Distance of a point from the line
	def distance(self, point):
		return self.a*point[0] + self.b*point[1] + self.c*point[2] + self.d
		
	
	

# A class that takes in a zglCamera and zglPerspective
# and generates the view frustum planes and tests objects
# whether they are within the 
#
class zglViewFrustumCulling:
	def __init__(self, perspective, camera):
		self.perspective = perspective
		self.camera = camera
		
		self.planes_initialized = False
		self.test_nearfar = False
		
	
	def update(self):
		self.updatePlanes()
		
	# Calculate the 6 planes that define the current view frustum
	def updatePlanes(self):
		camera_position = self.camera.position
		
		# unit direction vector of the camera direction and up vector
		camera_direction = zglVector.normalize( zglVector.subtract(self.camera.lookat, self.camera.position) )
		camera_up = zglVector.normalize(self.camera.up)
		
		# Top, bottom, left, right planes can be found simply using
		# the camera lookat vector, which is by definition in the center of 
		# the frustum.
		
		# First we need a vector pointing to the right:
		# This is simply the cross product of the camera's direction vector and its up vector
		camera_right = zglVector.crossProduct(camera_direction, camera_up)

		# Calculate the normals of each plane		
		#
		# we need one plane (either far or near) to generate normals for the 4 surround planes
		# so may as well use the far plane here:
		far_height = 2 * math.tan(self.perspective.fov/2) * self.perspective.far
		far_width = far_height * self.perspective.width/self.perspective.height
		
		# Center point for the far plane
		far_center = zglVector.add( self.camera.position, zglVector.multiplyConstant(camera_direction, self.perspective.far) )
		
		# Use the right edge of the far plane as reference point
		# to create a unit vector that lies along the right plane
		far_right = map(lambda i,j,k:  i + j*far_width/2 - k,
						far_center, camera_right, camera_position)
		far_right = zglVector.normalize(far_right)
		
		# Now we know both the far_right and the camera up vector are both on the right plane
		# So the normal is then simply the cross product of the two.
		# Note: take care with the order of the cross product to get the normal to
		# correctly point inwards.
		right_plane_normal = zglVector.crossProduct(camera_up, far_right)
		
		# Now do the same for the 3 other planes
		far_left = map(lambda i,j,k:  i - j*far_width/2 - k,
						far_center, camera_right, camera_position)
		far_left = zglVector.normalize(far_left)
		left_plane_normal = zglVector.crossProduct(far_left, camera_up)
		
		far_top = map(lambda i,j,k:  i + j*far_height/2 - k,
						far_center, camera_up, camera_position)
		far_top = zglVector.normalize(far_top)
		top_plane_normal = zglVector.crossProduct(far_top, camera_right)
		
		far_bottom = map(lambda i,j,k:  i - j*far_height/2 - k,
						far_center, camera_up, camera_position)
		far_bottom = zglVector.normalize(far_bottom)
		bottom_plane_normal = zglVector.crossProduct(camera_right, far_bottom)
		
		# Now we can create the planes!
		#
		self.top_plane = zglPlane.fromNormalAndPoint(top_plane_normal, self.camera.position)
		self.bottom_plane = zglPlane.fromNormalAndPoint(bottom_plane_normal, self.camera.position)
		self.left_plane = zglPlane.fromNormalAndPoint(left_plane_normal, self.camera.position)
		self.right_plane = zglPlane.fromNormalAndPoint(right_plane_normal, self.camera.position)
		
		self.planes_initialized = True
		
		if self.test_nearfar:
			# Now for Near and Far planes
			#
			# Near and far plane size
			near_height = 2 * math.tan(self.perspective.fov/2) * self.perspective.near
			near_width = near_height * self.perspective.width/self.perspective.height
			
			near_center = zglVector.add( self.camera.position, zglVector.multiplyConstant(camera_direction, self.perspective.near) )
	
			# Near plane points into the frustum (same as camera direction)
			self.near_plane = zglPlane.fromNormalAndPoint(camera_direction, near_center)
			# Far plane points towards the camera (negative camera direction)
			self.far_plane = zglPlane.fromNormalAndPoint(map(lambda i: -i, camera_direction), far_center)
		else:
			self.near_plane = None
			self.far_plane = None
	
	
	# Calculate planes using a matrix
	# The matrix has to be the ModelviewMatrix * ProjectionMatrix
	# (the order which OpenGL multiplies a vertex)
	#
	# The matrix is assumed to be column-major format (OpenGL standard)
	#
	# see: http://www.lighthouse3d.com/opengl/viewfrustum/index.php?clipspace
	def updatePlanesUsingMatrix(self, m):
		#	0	4	8	12
		#	1	5	9	13
		#	2	6	10	14
		#	3	7	11	15
		
		# Left Plane: col1 + col4
		self.left_plane = zglPlane( m[0] + m[12],
									m[1] + m[13],
									m[2] + m[14],
									m[3] + m[15] )
		# Right Plane: -col1 + col4
		self.right_plane = zglPlane( -m[0] + m[12],
									-m[1] + m[13],
									-m[2] + m[14],
									-m[3] + m[15] )
		# Top Plane: col2 + col4
		self.top_plane = zglPlane( m[4] + m[12],
									m[5] + m[13],
									m[6] + m[14],
									m[7] + m[15] )
		# Bottom Plane: -col2 + col4
		self.bottom_plane = zglPlane( -m[4] + m[12],
									-m[5] + m[13],
									-m[6] + m[14],
									-m[7] + m[15] )
		if self.test_nearfar:
			# Near plane: Col3 + Col4
			self.near_plane = zglPlane( m[8] + m[12],
										m[9] + m[13],
										m[10] + m[14],
										m[11] + m[15] )
			# Far plane: -Col3 + Col4
			self.far_plane = zglPlane( -m[8] + m[12],
										-m[9] + m[13],
										-m[10] + m[14],
										-m[11] + m[15] )
		else:
			self.near_plane = None
			self.far_plane = None

		
		
	# Test a point to see if we're inside the frustum
	# All plane normals are pointing inside the frustum, so the
	# distance test should all be positive for the point to
	# be inside
	#
	def containsPoint(self, point):
		if not self.planes_initialized:
			return True
	
		if (self.top_plane.distance(point) > 0
			and self.bottom_plane.distance(point) > 0
			and self.left_plane.distance(point) > 0
			and self.right_plane.distance(point) > 0
			
			# The above are the required tests. Sometimes we want to save
			# time and don't bother with near/far planes, because our scene
			# is wide/tall rather than deep
			and (self.near_plane is None or self.near_plane.distance(point) > 0)
			and (self.far_plane is None or self.far_plane.distance(point) > 0)
			):
			return True
			
		# One of the test failed
		return False
	
	
	def containsSphere(self, point, radius):
		if not self.planes_initialized:
			return True
			
 		if (self.top_plane.distance(point) > -radius
			and self.bottom_plane.distance(point) > -radius
			and self.left_plane.distance(point) > -radius
			and self.right_plane.distance(point) > -radius
			
			# The above are the required tests. Sometimes we want to save
			# time and don't bother with near/far planes, because our scene
			# is wide/tall rather than deep
			and (self.near_plane is None or self.near_plane.distance(point) > -radius)
			and (self.far_plane is None or self.far_plane.distance(point) > -radius)
			):
			return True
			
		# One of the test failed
		return False
		
	
	# Assumed to be a zglObject
	# and the object is assumed to have
	def containsObject(self, object):
		return self.containsSphere(object.position, object.getBoundingRadius())



#	Instead  of using planes to do culling
#	The radar approach is more efficient
#
class zglViewFrustumRadarCulling:
	def __init__(self, perspective, camera):
		self.perspective = perspective
		self.camera = camera
			
	# When perspective or camera has changed
	def update(self):
		self.z_axis = zglVector.normalize( zglVector.subtract(self.camera.lookat, self.camera.position) )
		self.x_axis = zglVector.normalize( zglVector.crossProduct(self.z_axis, self.camera.up) )
		self.y_axis = zglVector.crossProduct( self.x_axis, self.z_axis )
		
		# convert to radians
		fov = PI_OVER_180 * self.perspective.fov
		
		self.tan_fov = math.tan(fov/2)
		self.ratio = float(self.perspective.width)/self.perspective.height
		
		# for sphere test, need to multiply width and height by this to be
		# accurate. See: http://www.lighthouse3d.com/opengl/viewfrustum/index.php?camspace3
		self.sphere_factor_y = 1.0 / math.cos(fov)
		
		fov_x = math.atan(self.tan_fov * self.ratio)
		self.sphere_factor_x = 1.0 / math.cos(fov_x)

#		print "ratio = "+str(self.ratio)+" w,h="+str(self.perspective.width)+","+str(self.perspective.height)
#		print "fov = "+str(fov)+"  fov_x = "+str(fov_x)
#		print "sphere_factor_y = "+str(self.sphere_factor_y)+"  sphere_factor_x = "+str(self.sphere_factor_x)
		

	def containsPoint(self, point):
		# Vector from camera to point in question
		v = zglVector.subtract(point, self.camera.position)
		
		# Compute and test the z coordinate of the point, in the camera's frame of reference
		z = zglVector.dotProduct(v, self.z_axis)
		if z < self.perspective.near or z > self.perspective.far:
			return False
				
		# Using the z coordinate, we can then calculate the width and height of the frustum
		# at the current point
		half_height = z * self.tan_fov
		
		y = zglVector.dotProduct(v, self.y_axis)
		if y < -half_height or y > half_height:
			return False
		
		half_width = half_height * self.ratio
			
		x = zglVector.dotProduct(v, self.x_axis)
		if x < -half_width or x > half_width:
			return False
			
		return True
		
	
	def containsSphere(self, point, radius):
		# Vector from camera to point in question
		v = zglVector.subtract(point, self.camera.position)
		
		# Compute and test the z coordinate of the point, in the camera's frame of reference
		z = zglVector.dotProduct(v, self.z_axis)
		if z < self.perspective.near - radius or z > self.perspective.far + radius:
			return False
				
		# Using the z coordinate, we can then calculate the width and height of the frustum
		# at the current point
		half_height = z * self.tan_fov
		
		y = zglVector.dotProduct(v, self.y_axis)
		adjusted_radius = radius * self.sphere_factor_y
		if y < -half_height-adjusted_radius or y > half_height+adjusted_radius:
			return False
		
		half_width = half_height * self.ratio
			
		x = zglVector.dotProduct(v, self.x_axis)
		adjusted_radius = radius * self.sphere_factor_x
		if x < -half_width-adjusted_radius or x > half_width+adjusted_radius:
			return False
			
		return True
		
	# Assumed to be a zglObject
	# and the object is assumed to have
	def containsObject(self, object):
		return self.containsSphere(object.position, object.getBoundingRadius())

