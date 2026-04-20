#version 330

in vec3 vPosition;
in vec4 vColor;

out Vertex
{
	vec4 position;
	vec4 color;
} vertex;

uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;

void main()
{
	vertex.position = proj * view * model * vec4(vPosition, 1.0);
	vertex.color = vColor;

	gl_Position = vertex.position;
}