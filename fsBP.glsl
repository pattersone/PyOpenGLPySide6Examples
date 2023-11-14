#version 410 core

in vec3 normal_cam;
in vec3 pos_cam;

out vec4 frag_color;

uniform vec3 light_position;
uniform vec3 light_color;
uniform vec3 object_color;
uniform float shine;

uniform mat4 view;

void main()
{
    // Calculate the direction from the surface position to the light in "view coordinates."
    vec3 normal = normalize(normal_cam);
    vec3 light_position_view = vec3( view * vec4 (light_position, 1.0));
    vec3 light_direction = normalize(light_position_view - pos_cam);

    // In older Blinn-Phong model, "ambient" is a cheat for bounce lighting.    
    float ambient_strength = 0.2;
    vec3 ambient = ambient_strength * object_color;

    // The "diffuse" follows Lambert's (cosine) Law using the dot product of the normal and light direction.
    float diff = max(dot(normal, light_direction), 0.0);
    vec3 diffuse = diff * object_color;

    // The "specular" is view dependent and appears "half way" between the light direction and view direction.
    // It is raised to a power to create the peak, since it is usually many times brighter than the diffuse reflection.
    float spec_strength = 0.5;
    vec3 view_direction = normalize(-pos_cam);
    vec3 halfway_direction = normalize(light_direction + view_direction);
    float spec = pow(max(dot(normal, halfway_direction), 0.0), shine);
    vec3 specular = spec * light_color * spec_strength;

    vec3 result = ambient + diffuse + specular;

    frag_color = vec4(result, 1.0);
    //frag_color = vec4(normal_cam, 1.0);  // Uncomment line at left to see normals.
}


