#version 330

layout(location = 0) in vec3 vPosition;
layout(location = 1) in vec4 vColor;
layout(location = 2) in vec3 vNormal;
layout(location = 3) in vec4 vSkinWeights;
layout(location = 4) in vec4 vSkinBones;

uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;

uniform mat4 SkinningMatrices[128];

out Vertex
{
	vec4 position;
	vec4 color;
	vec4 normal;
} vertex;

void main()
{
	vec4 blendPos = vec4(0,0,0,0);
	vec4 blendNormal = vec4(0,0,0,0);
	int iMax = 4;
	if(vSkinWeights[0] + vSkinWeights[1] > 0.999)
		iMax = 2;
	
	int i;
	for (i = 0; i < iMax; ++i)
	{
		blendPos += SkinningMatrices[int(vSkinBones[i])] * vec4(vPosition, 1.0) * vSkinWeights[i];
		blendNormal += vec4(mat3(SkinningMatrices[int(vSkinBones[i])]) * vNormal * vSkinWeights[i],1);
	}

	vertex.position = view * model * blendPos;
	vertex.normal = normalize(view * model * blendNormal);	
	vertex.color = vColor;
	
	gl_Position = proj * vertex.position;
}
