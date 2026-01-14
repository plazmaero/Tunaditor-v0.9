#version 330 core

uniform sampler2D tex;
uniform float time;
uniform vec2 cam_pos;
uniform vec2 resolution;

const vec3 chroma_key = vec3(0.0, 0.0, 0.0);
const float threshold = 0.1;

in vec2 uvs;
out vec4 fragColor;

// Hash noise for clouds
float hash(vec2 p) {
    return fract(sin(dot(p, vec2(23.1, 91.7))) * 12345.6789);
}

// Simple 1D noise
float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);

    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));

    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

// Sky background
vec3 drawSky(vec2 uv) {
    float y = uv.y;
    return mix(vec3(0.5, 0.8, 1.0), vec3(0.1, 0.3, 0.6), y); // Top-down gradient
}

// Clouds layer
vec3 drawClouds(vec2 uv, float speed) {
    float cloud = noise(uv * 5.0 + vec2(time * speed, 0.0));
    cloud = smoothstep(0.5, 0.8, cloud);
    return mix(vec3(0.0), vec3(1.0), cloud * 0.5);
}

// Mountains layer
float drawMountains(vec2 uv, float offset) {
    uv.x += offset;
    float h = noise(vec2(uv.x * 1.5, 0.0)) * 0.25 + 0.25;
    return smoothstep(h, h - 0.05, uv.y);
}

void main() {
    vec2 fragCoord = uvs * resolution;
    vec2 uv = fragCoord / resolution;

    // Parallax offset for background based on cam_pos
    vec2 parallax_uv = uv + cam_pos * 0.001;

    // Background composition
    vec3 bg = drawSky(parallax_uv);

    // Far mountains (very slow movement)
    float m1 = drawMountains(parallax_uv * vec2(1.0, 1.0), time * 0.01);
    bg = mix(bg, vec3(0.2, 0.2, 0.3), m1);

    // Clouds (medium movement)
    vec3 cloud = drawClouds(parallax_uv * vec2(1.0, 0.5), 0.02);
    bg += cloud;

    // Sea at bottom
    if (uv.y > 0.75) {
        float wavy = sin((uv.x + time * 0.1) * 20.0) * 0.01;
        if (uv.y > 0.75 + wavy) {
            bg = mix(bg, vec3(0.1, 0.4, 0.8), 0.6);
        }
    }

    // Sample the foreground texture
    vec4 gameColor = texture(tex, uvs);
    float diff = distance(gameColor.rgb, chroma_key);

    // If chroma key, show bg instead
    fragColor = (diff < threshold)
        ? vec4(bg, 1.0)
        : gameColor;
}