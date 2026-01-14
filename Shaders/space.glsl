#version 330 core

uniform sampler2D tex;

uniform float time;
uniform vec2 resolution;
uniform float random_const;

const vec3 chroma_key = vec3(0.0549, 0.0549, 0.0549); 
const float threshold = 0.01;

in vec2 uvs;
out vec4 fragColor;


float hash(vec2 p) {
    // stable pseudo-random: same input => same output
    p = fract(p * 0.3183099 + random_const * 0.137);
    p += dot(p, p + 19.19);
    return fract(p.x * p.y);
}

vec3 starfield(vec2 uv) {
    float starDensity = 140.0;     // more = more stars
    float speed = 0.25;            // star forward speed

    // Shift UV downward over time
    uv.y += time * speed;

    // Scale UV to create many “cells”
    vec2 gridUV = uv * starDensity;

    // Integer cell
    vec2 cell = floor(gridUV);

    // Local position (0–1 inside the cell)
    vec2 cellUV = fract(gridUV);

    // Generate a random center position inside this cell
    vec2 starPos = vec2(hash(cell), hash(cell + 10.0));

    // Distance from star center
    float d = distance(cellUV, starPos);

    // Star radius 1–2 pixels depending on distance to camera (random)
    float pixelSize = 1.0 / resolution.y;   
    float radius = mix(5.0, 10.0, hash(cell + 20.0)) * pixelSize;

    // If within radius → bright star
    float star = smoothstep(radius, radius * 0.6, d);

    return vec3(star);
}


void main()
{
    vec2 fragCoord = uvs * resolution;
    vec2 uv = fragCoord / resolution;

    vec3 bg = vec3(0.01 * (uv.y + 0.3), 0.0 * (uv.y + 1.0), 0.03 * (uv.y + 0.85));


    bg += starfield(uv);
    bg += starfield(uv * 2.1 + 50.0) * 0.6;


    vec4 texColor = texture(tex, uvs);
    float diff = distance(texColor.rgb, chroma_key);
    if (diff < threshold) {fragColor = vec4(bg, 1.0);}
    else {fragColor = texColor;}
}