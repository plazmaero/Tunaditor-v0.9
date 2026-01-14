#version 330 core

uniform sampler2D tex;
uniform float time;
uniform vec2 cam_pos;

const vec3 chroma_key = vec3(0.0, 0.0, 0.0);
const float threshold = 0.1;

in vec2 uvs;
out vec4 fragColor;

float hash(float n) {return fract(sin(n) * 43758.5453123);}

vec3 starfield(vec2 uv) {
    uv = uv * 2.0 - 1.0;
    vec3 col = vec3(0.0);

    for (float i = 0.0; i < 100.0; i++) {
        float angle = hash(i) * 6.2831;
        float radius = hash(i + 1.0);

        vec2 dir = vec2(cos(angle), sin(angle));
        float speed = 1.5 + radius * 4.0;

        float t = mod(time * speed + radius * 5.0, 1.0);
        vec2 pos = dir * t;

        float d = length(uv - pos);
        float intensity = 0.01 / (d * d + 0.0005);

        float trail = smoothstep(0.03, 0.0, length(uv - pos + dir * 0.1));

        col += vec3(1.0) * intensity * trail;
    }

    return col;
}

void main() {
    vec4 texColor = texture(tex, uvs);

    // Compute distance to chroma key
    float diff = distance(texColor.rgb, chroma_key);

    // If close enough to the chroma key color, show stars
    if (diff < threshold) {
        vec3 stars = starfield(uvs);
        fragColor = vec4(stars, 1.0);
    } else {
        fragColor = texColor;
    }
}
