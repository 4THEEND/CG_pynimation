#version 330

in Vertex
{
	vec4 position;
	vec4 color;
} vertex;

out vec4 FragColor;
void main()
{
	FragColor = vertex.color;
}