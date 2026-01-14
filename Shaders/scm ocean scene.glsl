#version 330 core

uniform sampler2D tex;
uniform float time;
uniform vec2 cam_pos;
uniform vec2 resolution;
uniform float random_const;

const vec3 chroma_key = vec3(0.0549, 0.0549, 0.0549); 
const float threshold = 0.01;  

in vec2 uvs;
out vec4 fragColor;


float hash(vec2 p) {return fract(sin(dot(p, vec2(1270000 + (random_const * 5000), 3110000 + (random_const * 500) ))) * 43758.5453+ (random_const * 500) );}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f); //smoothstep curve

    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));

    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

vec3 sea(vec2 uv, vec2 cam_pos, float time, float seaLevel, float seaY) {
    float gradient = smoothstep(seaLevel, 0.8, seaY);
    vec3 baseColor = mix(vec3(0.2, 0.4, 1.0), vec3(0.0, 0.1, 0.8), gradient);

    float scale = mix(100.0 - ((seaY * (cam_pos.y / 1700)) * 30), 3.0, -1.5 - (0.0 - (seaY * (cam_pos.y / 1700))) - (seaY * 0.0001 * (cam_pos.y / 1700))); // Closer = larger
    float parallax = mix(1.0, 0.2, (uv.y * 10)); // Customize range if needed

    vec2 centeredUV = vec2(uv.x - 0.5, uv.y - 0.5);
    vec2 p = centeredUV * scale;

    // Apply parallax to cam scroll
    p.x += cam_pos.x * 0.001 * parallax;

    // Match vertical movement of sea + apply parallax
    p.y += ((cam_pos.y * 0.0001) + sin((uv.x + cam_pos.x * 0.0001) * 10.0 + time * 0.6) * 0.003) * parallax;

    float foamNoise = noise(vec2(p.x + (time - 125) * (50.5 * (uv.y + (cam_pos.y / 5000))), p.y * (uv.y * 10.0) * 0.1));
    float foam = smoothstep(0.6, 0.75, foamNoise);
    float foamFade = smoothstep(1.0, 0.1, 1.0 - (uv.y));

    float foamStrength = smoothstep(0.8, 0.2, 1.0 - (uv.y));
    return baseColor + foam * foamFade * foamStrength * vec3(0.1);
}




vec3 clouds(vec2 uv, vec2 cam_pos, float time) {
    if (uv.y > 0.4) return vec3(0.0);

    //World position for parallax and drifting
    vec2 p = vec2(uv.x * 30.0 + cam_pos.x * 0.001 + time, uv.y * 30.0 + cam_pos.y * 0.0004 + time / 5);

    //Cloud noise
    float n = 0.0;
    n += 0.9 * noise(p + vec2(time * 0.01, 0.0));
    n += 0.6 * noise(p * 2.0 + vec2(-time * 0.015, 0.0));
    n += 0.3 * noise(p * 4.0 + vec2(time * 0.02, 0.0));
    n = clamp(n - 0.4, 0.0, 1.0); // threshold and soften

    //Fade out of horizon
    float fade = smoothstep(0.4, -0.5, uv.y);
    n *= fade;

    vec3 cloudColor = vec3(1.0, 1.0, 0.97) * n;

    return cloudColor;
}




vec3 mountains(vec2 uv, vec2 cam_pos) {
   // World position for parallax movement
    vec2 world = uv * vec2(12.0, 1.0) + vec2(cam_pos.x * 0.0004, 0.0);

    // Basic height map with random jagged peaks
    float height = 0.0;
    float peak_spacing = 0.8;
    float peak_height = 0.025;

    float x = floor(world.x / peak_spacing);
    float local_x = fract(world.x / peak_spacing);

    // Random peak per segment (using random_const for variation)
    float h1 = hash(vec2(x, random_const)) * peak_height;
    float h2 = hash(vec2(x + 1.0, random_const)) * peak_height;

    // Sharp mountain shape (triangle interpolation)
    height = mix(h1, h2, local_x);
    height *= 3.0 - abs(2.0 * local_x - 1.0); // triangular peak shape

    // Flip so it rises from bottom
    height = 0.3 + height + ((1.0 - cam_pos.y) * 0.00002);

    // Smooth edge
    float edge = smoothstep(height, height - 0.01, uv.y);

    // Subtle blueish dark silhouette
    vec3 mountainColor = mix(vec3(-0.05), vec3(0.02, 0.05, 0.07), edge);
    return mountainColor;
}



vec3 sun(vec2 uv, float time) {
    // Sun position in UV space (top middle)
    vec2 sunPos = vec2(0.25, 0.1);

    // Radial distance from sun center
    float dist = distance(uv, sunPos);

    // Sun core
    float core = smoothstep(0.01, 0.005, dist);

    // Sun glow
    float glow = smoothstep(0.03, 0.001, dist);

    // Sun rays (soft rays based on angle)
    vec2 dir = normalize(uv - sunPos);
    float angle = atan(dir.y, dir.x);
    float rays = sin(angle * 12.0 + time * 10) * 0.03;
    rays *= smoothstep(0.8, 0.05, dist); // fade rays with distance

    vec3 sunColor = (vec3(2.5, 2.85, -0.1) * (core / 10.0)) + (vec3(2.5, 2.9, -0.5) * (glow / 5.0));
    sunColor += vec3(1.0, 0.85, 0.4) * rays;

    return sunColor;
}


vec3 underwater_rays(vec2 uv, float time) {
    vec2 sunPos = vec2(0.4, -2);
    float dist = distance(uv, sunPos);
    
    vec2 dir = normalize(uv - sunPos);
    float angle = atan(dir.y, dir.x);
    float rays = sin(angle * 12.0 + time) * 0.03;
    rays *= smoothstep(5.8, 5.05, dist);

    return vec3(-1.0) * rays;
}





void main() {
    vec2 fragCoord = uvs * resolution;
    vec2 uv = fragCoord / resolution;

    vec3 bg = vec3(0.2 * (uv.y + 0.7), 0.4 * (uv.y + 1.0), 0.7 * (uv.y + 1.6));
    
    bg += sun(uv, time);

    bg += clouds(uv, cam_pos, time);

    bg += mountains(uv, cam_pos);

    float seaLevel = 0.4;
    float seaY = uv.y + (cam_pos.y * 0.00002) + sin((uv.x + cam_pos.x * 0.0001) * 10.0 + time * 0.6) * 0.003;
    if (seaY > seaLevel) {bg = sea(uv, cam_pos, time, seaLevel, seaY);}
    
    if (cam_pos.y > 2000) {
        bg = vec3(0.2 - (uv.y + 0.7), 0.4 - (uv.y + 1.0), 0.4 * (uv.y + 1.6));
        bg += underwater_rays(uv, time);
    }

    vec4 texColor = texture(tex, uvs);
    float diff = distance(texColor.rgb, chroma_key);

    if (diff < threshold) {fragColor = vec4(bg, 1.0);}
    else {fragColor = texColor;}
}