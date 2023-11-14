#version 410 core

in vec3 normal_cam;
in vec3 pos_cam;

out vec4 frag_color;

uniform vec3 light_position;
uniform vec3 light_color;
uniform vec3 object_color;
uniform float roughness;
uniform float metal;
uniform float exposure;
uniform mat4 view;

const float PI = 3.14159265359;

float ggxNDF(float NdotH, float roughness) {
    float a = roughness * roughness;
    float a2 = a * a;
    float NdotH2 = NdotH * NdotH;
    float denom = (NdotH2 * (a2 - 1.0) + 1.0);
    return a2 / (PI * denom * denom);
}

vec3 fresnelSchlick(float cosTheta, vec3 F0) {
    return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);
}

float geometrySchlickGGX(float NdotV, float roughness) {
    float r = (roughness + 1.0);
    float k = (r * r) / 8.0;
    float nom = NdotV;
    float denom = NdotV * (1.0 - k) + k;
    return nom / denom;
}

float geometrySmith(vec3 N, vec3 V, vec3 L, float roughness) {
    float NdotV = max(dot(N, V), 0.0);
    float NdotL = max(dot(N, L), 0.0);
    float ggxV = geometrySchlickGGX(NdotV, roughness);
    float ggxL = geometrySchlickGGX(NdotL, roughness);
    return ggxV * ggxL;
}

float orenNayarDiffuse(float NdotV, float NdotL, vec3 N, vec3 L, vec3 V, float roughness) {
    float roughness_sq = roughness * roughness;
    float A = 1.0 - 0.5 * (roughness_sq / (roughness_sq + 0.33));
    float B = 0.45 * (roughness_sq / (roughness_sq + 0.09));

    float theta_i = acos(clamp(NdotL, -1.0, 1.0));
    float theta_r = acos(clamp(NdotV, -1.0, 1.0));
    float alpha = max(theta_i, theta_r);
    float beta = min(theta_i, theta_r);

    float gamma = dot(L - N * NdotL, V - N * NdotV);
    float C = max(0.0, gamma) * sin(alpha) * tan(beta);

    return max(0.0, NdotL * (A + B * C) / PI);
}

void main() {
    vec3 N = normalize(normal_cam);
    vec3 V = normalize(-pos_cam);
    vec3 L = normalize(vec3(view * vec4(light_position, 1.0)) - pos_cam);
    vec3 H = normalize(V + L);
    
    float NdotL = max(dot(N, L), 0.0);
    float NdotV = max(dot(N, V), 0.0);
    float NdotH = max(dot(N, H), 0.0);
    float HdotV = max(dot(H, V), 0.0);

    // Diffuse reflection (Lambertian)
    //vec3 diffuse = (1.0 - metal) * object_color / PI;

    // Diffuse reflection (Oren-Nayar)
    vec3 diffuse = (1.0 - metal) * object_color * orenNayarDiffuse(NdotV, NdotL, N, L, V, roughness);

    // Specular reflection (GGX)
    vec3 F0 = mix(vec3(0.04), object_color, metal);
    vec3 F = fresnelSchlick(HdotV, F0);
    float D = ggxNDF(NdotH, roughness);
    float G = geometrySmith(N, V, L, roughness);
    vec3 specular = D * F * G / (4.0 * NdotV * NdotL);

    vec3 result = (diffuse + specular) * light_color * NdotL;

    // Reinhard tone mapping.
    vec3 hdrColor = result * exposure;
    vec3 toneMappedColor = hdrColor / (hdrColor + vec3(1.0));

    frag_color = vec4(toneMappedColor, 1.0);
}











