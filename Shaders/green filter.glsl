#version 330 core

uniform sampler2D tex;

in vec2 uvs;
out vec4 fragColor;

void main()
{
    fragColor = vec4(0.0, texture(tex, uvs).g, 0.0, 1.0);
}