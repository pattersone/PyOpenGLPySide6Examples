import sys
import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QSurfaceFormat, QMatrix4x4
from PySide6.QtOpenGL import QOpenGLShaderProgram, QOpenGLShader
from OpenGL import GL

class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)

    def initializeGL(self):
        self.shader_program = QOpenGLShaderProgram()
        self.shader_program.addShaderFromSourceFile(QOpenGLShader.Vertex, "vs.glsl")
        self.shader_program.addShaderFromSourceFile(QOpenGLShader.Fragment, "fs.glsl")
        self.shader_program.link()

        vertices = np.array([
            # Positions         # Colors
            0.0,  1.0, 0.0,     1.0, 0.0, 0.0,  # Red vertex
            -1.0, -1.0, 0.0,    0.0, 1.0, 0.0,  # Green vertex
            1.0, -1.0, 0.0,     0.0, 0.0, 1.0   # Blue vertex
        ], dtype=np.float32)

        self.vao = GL.glGenVertexArrays(1) 
        GL.glBindVertexArray(self.vao)

        self.vertex_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices.tobytes(), GL.GL_STATIC_DRAW)

        GL.glClearColor(0.2, 0.2, 0.2, 1.0)  

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT) 
        self.shader_program.bind()

        position_attr = self.shader_program.attributeLocation("position")
        color_attr = self.shader_program.attributeLocation("color")

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer)
        self.shader_program.enableAttributeArray(position_attr)
        self.shader_program.enableAttributeArray(color_attr)
        self.shader_program.setAttributeBuffer(position_attr, GL.GL_FLOAT, 0, 3, 6 * 4) 
        self.shader_program.setAttributeBuffer(color_attr, GL.GL_FLOAT, 3 * 4, 3, 6 * 4)
 
        self.shader_program.setUniformValue("model", QMatrix4x4())
        self.shader_program.setUniformValue("view", QMatrix4x4()) 
        self.shader_program.setUniformValue("projection", QMatrix4x4()) 

        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)

        GL.glDisableVertexAttribArray(position_attr)
        GL.glDisableVertexAttribArray(color_attr)

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

