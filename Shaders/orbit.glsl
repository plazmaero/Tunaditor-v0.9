#version 330 core

uniform sampler2D tex;
uniform float time;

in vec2 uvs;
out vec4 f_color;

void main() {
    float angle = time;
    vec2 sample_pos = vec2(uvs.x + cos(angle) * 1, uvs.y + sin(angle) * 1);
    f_color = vec4(texture(tex, sample_pos).rgb, 1.0);
}