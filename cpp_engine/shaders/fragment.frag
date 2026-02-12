#version 330 core
out vec4 FragColor;

in vec3 Normal;
in vec3 FragPos;

void main() {
    vec3 baseColor = gl_FrontFacing ? vec3(1.0, 0.0, 0.0) : vec3(1.0, 1.0, 1.0);
    
    float ambientStrength = 0.2;
    vec3 ambient = ambientStrength * vec3(1.0, 1.0, 1.0);
  	
    vec3 norm = normalize(Normal);
    if (!gl_FrontFacing) norm = -norm;
    
    vec3 lightDir = normalize(vec3(0.1, 0.96, 0.2));
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * vec3(1.0, 1.0, 1.0);
    
    vec3 result = (ambient + diffuse) * baseColor;
    FragColor = vec4(result, 1.0);
}