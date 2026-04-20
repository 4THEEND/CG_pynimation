#version 330

in vec3 vPosition;
in vec2 vTextCoord;

out vec2 texture_coordinates;

uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;

void main()
{
	gl_Position = proj * view * model * vec4(vPosition.x, vPosition.y, vPosition.z, 1.0);
	texture_coordinates = vTextCoord;
}