import sys
import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QSurfaceFormat, QVector3D
from PySide6.QtOpenGL import QOpenGLVertexArrayObject, QOpenGLShaderProgram, QOpenGLShader
from OpenGL import GL
from objLoader import OBJLoader

class GLWidget(QOpenGLWidget):
    # Constructor
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        # MVP Matrices set to be same type OpenGL accepts, 32-bit floats.
        self.model_matrix = np.identity(4, dtype=np.float32)
        self.view_matrix = np.identity(4, dtype=np.float32)
        self.projection_matrix = np.identity(4, dtype=np.float32)
        self.fov = 45 # degrees
        self.vertex_count = 0

    # Setup OpenGL data and state.
    def initializeGL(self):
        # Setup shader program(s) used.
        self.shader_program = QOpenGLShaderProgram()
        self.shader_program.addShaderFromSourceFile(QOpenGLShader.Vertex, "vsobj.glsl")
        self.shader_program.addShaderFromSourceFile(QOpenGLShader.Fragment, "fsBP.glsl")
        self.shader_program.link()

        # Setup geometry by loading teapot.obj using objLoader.py.
        obj_loader = OBJLoader()
        obj_loader.load("teapot.obj")

        # Interleaving vertex attributes reduces cache misses.  
        modelData = obj_loader.get_interleaved_data()

        # Divide by (3 for vert + 3 for norm) to get count for draw.
        self.vertex_count = len(modelData) // 6

        # Create and bind Vertex Array Object (VAO).
        self.vao = GL.glGenVertexArrays(1) 
        GL.glBindVertexArray(self.vao)

        # Generate, bind, and pass data for Vertex Buffer Object (VBO).
        self.vertex_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, modelData.nbytes, modelData.tobytes(), GL.GL_STATIC_DRAW)

        # Model Matrix 
        model_yaw = 90.0 # degrees
        identity_mat4 = np.identity(4, dtype=np.float32)	
        R = self.rotate_y_deg(identity_mat4, model_yaw)
        self.model_matrix = np.dot(R, identity_mat4)

        # View Matrix
        cam_pos = np.array([0.0, 1.0, 4])  
        cam_yaw = 0.0 # degrees
        identity_mat4 = np.identity(4, dtype=np.float32)
        T = self.translate(identity_mat4, -cam_pos)
        R = self.rotate_y_deg(identity_mat4, -cam_yaw)
        self.view_matrix = np.dot(R, T)        

        # Projection Matrix
        self.setupProjectionMatrix(self.width(), self.height())

        # General stuff including enabling dark gray to debug visually more easily.
        # Note:  Should normally unbind VAO and rebind particular one during paintGL but will keep simple here.
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glClearColor(0.2, 0.2, 0.2, 1.0)  


    # Utility functions

    def setupProjectionMatrix(self, width, height):
        aspect_ratio = width / height

        # Setup near and far clipping planes, fov in radians, and aspect ratio.
        near, far = 0.1, 100.0
        fov  = np.radians(self.fov)
        aspect_ratio = width / height  

       # Setup Projection Matrix by scaling dimensions based on fov, aspect, and frustum depth.
        range = np.tan(fov * 0.5) * near
        Sx = (2.0 * near) / (range * aspect_ratio + range * aspect_ratio)
        Sy = near / range
        Sz = -(far + near) / (far - near)
        Pz = -(2.0 * far * near) / (far - near)
        self.projection_matrix = np.array([
            [Sx,  0.0, 0.0,  0.0],
            [0.0, Sy,  0.0,  0.0],
            [0.0, 0.0, Sz,    Pz],
            [0.0, 0.0, -1.0, 0.0]    
        ], dtype=np.float32)
        
    def translate(self, identity, vec):
        T = np.copy(identity)
        T[:3, 3] = vec
        return T
    
    def rotate_y_deg(self, identity, angle_deg):
        angle_rad = np.radians(angle_deg)
        cos_angle, sin_angle = np.cos(angle_rad), np.sin(angle_rad)
        R = np.copy(identity)
        R[0, 0], R[0, 2] = cos_angle, sin_angle
        R[2, 0], R[2, 2] = -sin_angle, cos_angle
        return R


    # Refresh GL context on window re-size.
    def resizeGL(self, width, height):
        self.setupProjectionMatrix(width, height)
        GL.glViewport(0, 0, width, height)

    # Draw calls.
    def paintGL(self):
        self.shader_program.bind()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  

        # Locate references to shader attributes and uniforms.  
        prog = self.shader_program.programId()
        mloc = GL.glGetUniformLocation(prog, "model")
        vloc = GL.glGetUniformLocation(prog, "view")
        ploc = GL.glGetUniformLocation(prog, "projection")
        lploc = GL.glGetUniformLocation(prog, "light_position")
        lcloc = GL.glGetUniformLocation(prog, "light_color")
        ocloc = GL.glGetUniformLocation(prog, "object_color")
        sloc = GL.glGetUniformLocation(prog, "shine")

        position_attr = self.shader_program.attributeLocation("position")  
        normal_attr = self.shader_program.attributeLocation("normal")
        self.shader_program.enableAttributeArray(position_attr)
        self.shader_program.enableAttributeArray(normal_attr)
        self.shader_program.setAttributeBuffer(position_attr, GL.GL_FLOAT, 0, 3, 6 * 4)
        self.shader_program.setAttributeBuffer(normal_attr, GL.GL_FLOAT, 3 * 4, 3, 6 * 4)

        # Pass MVP to vertex shader.
        # Compose matrices visually as if column order, but Numpy internally stores as row-major versus OpenGL's column major, hence transpose.
        GL.glUniformMatrix4fv(mloc, 1, GL.GL_FALSE, self.model_matrix.T.astype(np.float32))
        GL.glUniformMatrix4fv(vloc, 1, GL.GL_FALSE, self.view_matrix.T.astype(np.float32))
        GL.glUniformMatrix4fv(ploc, 1, GL.GL_FALSE, self.projection_matrix.T.astype(np.float32))

        # Pass rest of uniform parameter values to fragment shader.
        GL.glUniform3f(lploc, 10.0, 10.0, 3.0)
        GL.glUniform3f(lcloc, 1.0, 1.0, 1.0)
        GL.glUniform3f(ocloc, 0.965, 0.404, 0.2)
        GL.glUniform1f(sloc, 10.0)

        # Draw and normally unbind and disable after but keeping simple.
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.vertex_count)

        self.shader_program.release()



#################################################################
# Main
#################################################################

# Set the surface format before creating the application instance
format = QSurfaceFormat()
format.setVersion(4, 1)
format.setProfile(QSurfaceFormat.CoreProfile)
format.setSamples(4)
QSurfaceFormat.setDefaultFormat(format)

# Create and show the application and widget
app = QApplication([])
w = GLWidget()
w.show()
app.exec()












