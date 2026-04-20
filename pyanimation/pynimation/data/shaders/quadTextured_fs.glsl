#version 330

in vec2 texture_coordinates;
uniform vec4 colorIn;
uniform float mixParameter;
uniform sampler2D basicTexture;

void main()
{
    vec4 texture_color = texture2D (basicTexture, texture_coordinates);
    vec4 mixed_color = mix( colorIn, texture_color , mixParameter);
	gl_FragColor = mixed_color;
}