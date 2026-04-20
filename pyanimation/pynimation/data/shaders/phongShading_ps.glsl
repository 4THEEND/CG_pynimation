#version 330

in Vertex
{
	vec4 position;
	vec4 color;
	vec4 normal;
} vertex;

uniform mat4 view;

uniform vec3 lightDirection;
uniform vec3 lightSpecular;
uniform vec3 lightDiffuse;
uniform vec3 lightAmbient;

// surface reflectance
uniform vec4 Ks = vec4 (1.0, 1.0, 1.0, 100.0); // fully reflect specular light
uniform vec3 Kd = vec3 (1.0, 1.0, 1.0); // diffuse surface reflectance
uniform vec3 Ka = vec3 (1.0, 1.0, 1.0); // fully reflect ambient light

out vec4 FragColor;

void main()
{
	vec3 vNormal = normalize(vertex.normal.xyz);
	// ambient intensity
	vec3 Ia = lightAmbient * Ka;

	// diffuse intensity
	vec3 dir_light_eye = normalize (-lightDirection);
	float dot_prod = dot (dir_light_eye, vNormal);
	dot_prod = max (dot_prod, 0.0);
	vec3 Id = lightDiffuse * vertex.color.xyz * Kd * dot_prod; // final diffuse intensity
	
	// specular intensity
	vec3 reflection_eye = reflect (-dir_light_eye, vNormal);
	vec3 surface_to_viewer_eye = normalize (-vertex.position.xyz);
	float dot_prod_specular = dot (reflection_eye, surface_to_viewer_eye);
	dot_prod_specular = max (dot_prod_specular, 0.0);
	float specular_factor = pow (dot_prod_specular, Ks.w);
	vec3 Is = lightSpecular * Ks.xyz * specular_factor; // final specular intensity
	
	// final colour
	FragColor = vec4 (Is + Id + Ia, 1.0);
}