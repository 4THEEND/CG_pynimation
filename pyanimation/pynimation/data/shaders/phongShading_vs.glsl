#version 330

layout(location = 0) in vec3 vPosition;
layout(location = 1) in vec4 vColor;
layout(location = 2) in vec3 vNormal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;

out Vertex
{
	vec4 position;
	vec4 color;
	vec4 normal;
} vertex;

void main()
{
	vertex.position = view * model * vec4(vPosition, 1.0);
	vertex.color = vColor;
	vertex.normal = normalize(view * model * vec4(vNormal, 0.0));
	gl_Position = proj * vertex.position;
}