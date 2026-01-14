#version 330 core

uniform sampler2D tex;
uniform float time;
uniform vec2 resolution;

in vec2 uvs;
out vec4 fragColor;

void main()
{
    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = uvs / resolution;

    // Time varying pixel color
    vec3 col = 0.5 + 0.5 * cos(time + uv.xyx + vec3(0, 2, 4));

    // Output to screen
    fragColor = vec4(col / texture(tex, uvs).rgb, 1.0);
}