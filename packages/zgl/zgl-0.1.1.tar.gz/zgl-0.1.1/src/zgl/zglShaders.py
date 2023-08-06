import os, string
from OpenGL.GL import *
from OpenGL.GLUT import *
from zglUtils import *

# General shader class
class zglShaders:
	use_GL_functions = isFunctionAvailable("glCreateProgram");
	use_ARB_functions = False;
	
	def __init__(self):
		self.program_id = -1
		
		self.program_id = glCreateProgram()

	
	def useVertexShader(self, shader_file):
		file = open(shader_file, 'r')
		shader_source = file.read()
		
		vertex_shader_id = glCreateShader(GL_VERTEX_SHADER);
		glShaderSource(vertex_shader_id, shader_source);
		glCompileShader(vertex_shader_id);
#		self.vertex_shader_id = vertex_shader_id
		glAttachShader(self.program_id, vertex_shader_id)
	
	
	def useFragmentShader(self, shader_file):
		file = open(shader_file, 'r')
		shader_source = file.read()
		
		fragment_shader_id = glCreateShader(GL_FRAGMENT_SHADER);
		glShaderSource(fragment_shader_id, shader_source);
		glCompileShader(fragment_shader_id);
#		self.fragment_shader_id = fragment_shader_id
		glAttachShader(self.program_id, fragment_shader_id)
		
	
		

class zglShaderManager:
	vertex_shaders = { }
	fragment_shaders = { }
	
	def getVertexShader(self, vertex_shader_file):
		file = open(vertex_shader_file, 'r')
		shader_source = file.read()
		
		vertex_shader_id = glCreateShader(GL_VERTEX_SHADER);
		glShaderSource(vertex_shader_id, shader_source);
		glCompileShader(vertex_shader_id);
		
		vertex_shaders[vertex_shader_id] = vertex_shader_id
