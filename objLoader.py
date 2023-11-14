import numpy as np

class OBJLoader:
    def __init__(self):
        self.vertices = []
        self.normals = []
        self.vertex_indices = []
        self.normal_indices = []  # Add a new list for normal indices
        self.faces = []  # Initialize a list to store faces

    def load(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                if line.startswith('v '):
                    self.vertices.extend(map(float, line.strip().split()[1:4]))
                elif line.startswith('vn '):
                    self.normals.extend(map(float, line.strip().split()[1:4]))
                elif line.startswith('f '):
                    face = line.strip().split()[1:]
                    vertex_indices = []
                    normal_indices = []  # Add a list to store normal indices
            
                    for vertex_data in face:
                        vertex_parts = vertex_data.split('/')
                        
                        # Ensure there are at least two elements (vertex and normal)
                        if len(vertex_parts) >= 1:
                            vertex_index = int(vertex_parts[0])
                            vertex_indices.append(vertex_index)
                            
                        # Check if a normal index is provided (len >= 3)
                        if len(vertex_parts) >= 3:
                            normal_index = int(vertex_parts[2])
                            normal_indices.append(normal_index)  # Store normal indices
            
                    if len(vertex_indices) == 3:
                        self.vertex_indices.append(vertex_indices)
                        self.normal_indices.append(normal_indices)  # Store normal indices
                        self.faces.append([vertex_indices, normal_indices])
                    elif len(vertex_indices) == 4:
                        # Convert quads to triangles 
                        # (first triangle)
                        self.vertex_indices.append([vertex_indices[0], vertex_indices[1], vertex_indices[2]])
                        self.normal_indices.append([normal_indices[0], normal_indices[1], normal_indices[2]])
                        # (second triangle)
                        self.vertex_indices.append([vertex_indices[2], vertex_indices[3], vertex_indices[0]])
                        self.normal_indices.append([normal_indices[2], normal_indices[3], normal_indices[0]])
                        self.faces.append([vertex_indices, normal_indices])

    def get_vertex_data(self):
        vertices = []
        for vertex_index in self.vertex_indices:
            for idx in vertex_index:
                vertices.extend(self.vertices[(idx - 1) * 3: idx * 3])
        return np.array(vertices, dtype=np.float32)

    def get_normal_data(self):
        normals = []
        for normal_index in self.normal_indices:
            for idx in normal_index:
                normals.extend(self.normals[(idx - 1) * 3: idx * 3])
        return np.array(normals, dtype=np.float32)

    def get_interleaved_data(self):
        interleaved_data = []
        for face in self.faces:
            for vertex_index, normal_index in zip(face[0], face[1]):
                # Calculate indices
                vertex_index -= 1
                normal_index -= 1

                # Extract vertex and normal data
                vertex = self.vertices[vertex_index * 3: (vertex_index + 1) * 3]
                normal = self.normals[normal_index * 3: (normal_index + 1) * 3]

                # Append to interleaved data
                interleaved_data.extend(vertex)
                interleaved_data.extend(normal)

        return np.array(interleaved_data, dtype=np.float32)

