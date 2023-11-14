from PySide6.QtWidgets import QApplication
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QSurfaceFormat
from OpenGL import GL

class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)

    def initializeGL(self):
        GL.glClearColor(0.8, 0.8, 0.8, 1.0)

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

