#version 330 core

uniform sampler2D tex;
uniform float time;
uniform vec2 resolution;
uniform float random_const;
uniform int player_in_amount;

const vec3 chroma_key = vec3(0.0549, 0.0549, 0.0549); 
const float threshold = 0.01;

in vec2 uvs;
out vec4 fragColor;



float rand(vec2 coord)
{
    float a = 12.9898;
    float b = 78.233;
    float c = 43758.5453;
    return fract(sin(dot(coord.xy , vec2(a, b)) + random_const) * c);
}

float smoothRand(vec2 uv) {
    vec2 i = floor(uv);
    vec2 f = fract(uv);
    
    float a = rand(i);
    float b = rand(i + vec2(1.0, 0.0));
    float c = rand(i + vec2(0.0, 1.0));
    float d = rand(i + vec2(1.0, 1.0));
    
    // bilinear interpolation
    float u = f.x * f.x * (3.0 - 2.0 * f.x);
    float v = f.y * f.y * (3.0 - 2.0 * f.y);
    return mix(a, b, u) * (1.0 - v) + mix(c, d, u) * v;
}



void main()
{
    vec2 fragCoord = uvs * resolution;
    vec2 uv = fragCoord / resolution;

    vec3 bg = vec3(0.05 * (uv.y + 0.7), 0.04 * (uv.y + 1.0), 0.06 * (uv.y + 0.85));


    //MOVİNG STONE TEXTURE
    float speed1 = 8.0;
    float speed2 = 14.0;

    float tileSize1 = 32.0;
    vec2 tileUV1 = mod(fragCoord.xy + vec2(time * speed1, time * 0.5) + random_const, tileSize1) / tileSize1;
    float n1 = smoothRand(tileUV1 * 20.0 + random_const);
    vec3 stoneColor1 = vec3(
        0.08 + 0.03 * n1 + (uv.y / 20.0),
        0.10 * n1 + (uv.y / 20.0),
        0.10 * n1 + (uv.y / 20.0)
    );

    float tileSize2 = 64.0; // smaller tiles = higher frequency
    vec2 tileUV2 = mod(fragCoord.xy * 1.3 + vec2(time * speed2, -time * 1.7) + random_const * 23.0, tileSize2) / tileSize2;
    float n2 = smoothRand(tileUV2 * 30.0 + random_const * 2.0);
    vec3 stoneColor2 = vec3(
        0.06 + 0.04 * n2 + (uv.y / 18.0),
        0.08 * n2 + (uv.y / 18.0),
        0.08 * n2 + (uv.y / 18.0)
    );

    vec3 stoneColor = mix(stoneColor1, stoneColor2, 0.5);
    bg += stoneColor;


    // TUNA COLOR BANDS
    float travelTime = 2.0;
    float t = mod(time, travelTime) / travelTime;
    float eased = 1.0 - pow(1.0 - t, 2.0);
    float flashPos = mix(1.5, -0.5, eased);

    float flash = exp(-10.0 * pow(uv.x - flashPos, 2.0));

    float pulse = 0.2 + 0.05 * sin(time * 4.0);
    vec3 flashColor = vec3(pulse) * (flash / 2) * 0.6;
    if (0.14 < uv.y && uv.y < 0.31) {bg = (uv.x / 10) + vec3(0.01, 0.07, 0.35) / 2; bg += flashColor;}
    if (0.31 < uv.y && uv.y < 0.33) {bg = (uv.x / 10) + vec3(0.83, 0.65, 0.03) / 2; bg += flashColor;}
    if (0.33 < uv.y && uv.y < 0.50) {bg = (uv.x / 10) + vec3(0.21, 0.22, 0.23) / 2; bg += flashColor;}
    if (0.60 < uv.y && uv.y < 0.98) {bg = vec3(0.02 + (uv.x / 31), 0.02 + (uv.x / 32), 0.03 + (uv.x / 30)); bg *= 3 + 0.2 * sin(fragCoord.y);}



    // CHARACTER CUTOUT
    if (0.60 < uv.y && uv.y < 0.98) {
        int slotCount = 4;
        float slotWidth = 1.0 / float(slotCount);

        vec3 slotColors[4];
        slotColors[0] = vec3(0.8, 0.0, 0.0); // red
        slotColors[1] = vec3(0.0, 0.0, 0.8); // blue
        slotColors[2] = vec3(0.0, 0.8, 0.0); // green
        slotColors[3] = vec3(0.8, 0.8, 0.0); // yellow

        float marginX = 0.02;
        float marginY = 0.03;
        float borderThickness = 0.02;
        float soft = 0.02;

        for (int i = 0; i < slotCount; i++) {
            float x0 = float(i) * slotWidth + marginX;
            float x1 = float(i + 1) * slotWidth - marginX;
            float y0 = 0.60 + marginY;
            float y1 = 0.98 - marginY;

            if (uv.x >= x0 && uv.x <= x1 && uv.y >= y0 && uv.y <= y1) {
                vec3 borderColor = slotColors[i];

                // Distance to nearest corner
                float dx = min(uv.x - x0, x1 - uv.x);
                float dy = min(uv.y - y0, y1 - uv.y);
                float dist = min(dx, dy);

                // Smooth mask for rounded corners
                float mask = smoothstep(0.0, soft, dist);

                // Border detection
                if (uv.x < x0 + borderThickness || uv.x > x1 - borderThickness ||
                    uv.y < y0 + borderThickness || uv.y > y1 - borderThickness) {
                    bg = borderColor * mask;
                } else {
                    if (i < player_in_amount) {bg = 0.3 * borderColor * mask;}
                    else {bg = vec3(0.0) * mask;}
                }
            }
        }
    }

    
    // SUBTLE PULSİNG VİGNETTE
    float gradient_pulse = smoothstep(0.3, 0.9, length(uv - vec2(0.5))) * (0.4 + 0.6 * sin(time * 1.5));
    bg -= vec3(0.075, 0.075, 0.075) * gradient_pulse;


    vec4 texColor = texture(tex, uvs);
    float diff = distance(texColor.rgb, chroma_key);
    if (diff < threshold) {fragColor = vec4(bg, 1.0);}
    else {fragColor = texColor;}
}