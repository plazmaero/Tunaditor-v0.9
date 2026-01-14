#version 330 core

uniform sampler2D tex;
uniform float time;

in vec2 uvs;
out vec4 f_color;

void main() {
    float angle = time * 50;
    vec2 sample_pos = vec2(pow(uvs.x + time, 2) / 2, pow(uvs.y + time, 2) / 2);
    f_color = vec4(texture(tex, sample_pos).rgb, 1.0);
}