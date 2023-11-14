#version 410 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 normal_cam, pos_cam;

void main()
{
    vec4 view_position = view * model * vec4(position, 1.0);
    pos_cam = vec3 (view * model * vec4 (position, 1.0)); 
    gl_Position = projection * view_position;
    normal_cam = normalize(vec3 (view * model * vec4(normal, 0.0)));
}

