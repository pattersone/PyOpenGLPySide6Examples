import sys
import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtOpenGL import QOpenGLVertexArrayObject, QOpenGLShaderProgram, QOpenGLShader
from OpenGL import GL

class GLWidget(QOpenGLWidget):
    # Constructor
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        # MVP Matrices set to be same type OpenGL accepts, 32-bit floats.
        self.model_matrix = np.identity(4, dtype=np.float32)
        self.view_matrix = np.identity(4, dtype=np.float32)
        self.projection_matrix = np.identity(4, dtype=np.float32)
        self.fov = 45 # degrees

    # Setup OpenGL data and state.
    def initializeGL(self):
        # Setup shader program(s) used.
        self.shader_program = QOpenGLShaderProgram()
        self.shader_program.addShaderFromSourceFile(QOpenGLShader.Vertex, "vs.glsl")
        self.shader_program.addShaderFromSourceFile(QOpenGLShader.Fragment, "fs.glsl")
        self.shader_program.link()

        # Setup geometry.
        vertices = np.array([
            # Positions         # Colors
            0.0,  0.5, 0.0,     1.0, 0.0, 0.0,  # Red vertex
            -0.5, -0.5, 0.0,    0.0, 1.0, 0.0,  # Green vertex
            0.5, -0.5, 0.0,     0.0, 0.0, 1.0   # Blue vertex
        ], dtype=np.float32)

        # Create and bind Vertex Array Object (VAO).
        self.vao = GL.glGenVertexArrays(1) 
        GL.glBindVertexArray(self.vao)

        # Generate, bind, and pass data for Vertex Buffer Object (VBO).
        self.vertex_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices.tobytes(), GL.GL_STATIC_DRAW)

        # Model Matrix is set to identity in constructor.

        # View Matrix
        cam_pos = np.array([0.0, 0.0, 8])  
        cam_yaw = 25.0 # degrees
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
        ploc = GL.glGetUniformLocation(prog, "projection")
        vloc = GL.glGetUniformLocation(prog, "view")

        position_attr = self.shader_program.attributeLocation("position")  
        color_attr = self.shader_program.attributeLocation("color")
        self.shader_program.enableAttributeArray(position_attr)
        self.shader_program.enableAttributeArray(color_attr)
        self.shader_program.setAttributeBuffer(position_attr, GL.GL_FLOAT, 0, 3, 6 * 4)
        self.shader_program.setAttributeBuffer(color_attr, GL.GL_FLOAT, 3 * 4, 3, 6 * 4)

        # Pass MVP to vertex shader.
        # Compose matrices visually as if column order, but Numpy internally stores as row-major versus OpenGL's column major, hence transpose.
        GL.glUniformMatrix4fv(mloc, 1, GL.GL_FALSE, self.model_matrix.T.astype(np.float32))
        GL.glUniformMatrix4fv(vloc, 1, GL.GL_FALSE, self.view_matrix.T.astype(np.float32))
        GL.glUniformMatrix4fv(ploc, 1, GL.GL_FALSE, self.projection_matrix.T.astype(np.float32))

        # Draw and normally unbind and disable after but keeping simple.
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)

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












