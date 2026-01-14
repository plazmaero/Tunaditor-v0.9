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
    p = fract(p * 0.3183099 + random_const * 0.137);
    p += dot(p, p + 19.19);
    return fract(p.x * p.y);
}

vec3 starfield(vec2 uv) {
    //speed
    uv.y += time * 0.65;

    //scaling the UV by the density to make cells
    vec2 gridUV = uv * 10.0;
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


// Simple smooth pseudo-noise
float noise(vec2 p){
    vec2 i = floor(p);
    vec2 f = fract(p);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    vec2 u = f*f*(3.0-2.0*f); // smoothstep interpolation
    return mix(a, b, u.x) + (c - a)*u.y*(1.0 - u.x) + (d - b)*u.x*u.y;
}

vec3 nebula(vec2 uv, float t) {
    // ---------- Scroll ----------
    uv += vec2(0.0, t * 0.01);

    // ---------- Determine minute phase ----------
    float minute = floor(t / 60.0);
    float localTime = fract(t / 60.0); // 0->1 within the minute

    // ---------- Random color per minute ----------
    vec3 colA = vec3(hash(vec2(minute, 1.0)),
                     hash(vec2(minute, 2.0)),
                     hash(vec2(minute, 3.0)));
    vec3 colB = vec3(hash(vec2(minute+1.0, 1.0)),
                     hash(vec2(minute+1.0, 2.0)),
                     hash(vec2(minute+1.0, 3.0)));
    vec3 color = mix(colA, colB, localTime) * 0.3; // soft intensity

    // ---------- Noise for soft, organic shape ----------
    float n = 0.0;
    float scale = 0.5 + hash(vec2(minute,5.0)); // shape varies each minute
    for(int i=0; i<4; i++){
        n += noise(uv * scale) / scale;
        scale *= 2.0;
    }
    n = smoothstep(0.2, 0.8, n * 0.5 + 0.25);

    return color * n; // final soft nebula
}





void main()
{
    vec2 fragCoord = uvs * resolution;
    vec2 uv = fragCoord / resolution;

    vec3 bg = vec3(0.01 * (uv.y + 0.3), 0.0 * (uv.y + 1.0), 0.03 * (uv.y + 0.85));


    bg += nebula(uv, time);

    bg += starfield(uv * 5.0) * 0.6;
    bg += starfield(uv * 4.0) * 0.6;
    bg += starfield(uv * 3.0) * 0.6;
    bg += starfield(uv * 2.0) * 0.6;
    bg += starfield(uv * 1.0) * 0.6;


    vec4 texColor = texture(tex, uvs);
    float diff = distance(texColor.rgb, chroma_key);
    if (diff < threshold) {fragColor = vec4(bg, 1.0);}
    else {fragColor = texColor;}
}