#version 330

in vec2 texture_coordinates;
uniform sampler2D basic_texture;

void main()
{
	gl_FragColor = texture2D (basic_texture, texture_coordinates);
}