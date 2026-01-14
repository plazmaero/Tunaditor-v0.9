#version 330 

uniform sampler2D tex;

in vec2 uvs;
out vec4 fragColor;

vec3 aces(vec3 x) {
  const float a = 2.51;
  const float b = 0.03;
  const float c = 2.43;
  const float d = 0.59;
  const float e = 0.14;
  return clamp((x * (a * x + b)) / (x * (c * x + d) + e), 0.0, 1.0);
}

uniform float gamma = 0.6;
uniform float numColors = 16;

uniform float time;//

vec3 hueShift( vec3 color, float hueAdjust ){

    const vec3  kRGBToYPrime = vec3 (0.299, 0.587, 0.114);
    const vec3  kRGBToI      = vec3 (0.596, -0.275, -0.321);
    const vec3  kRGBToQ      = vec3 (0.212, -0.523, 0.311);

    const vec3  kYIQToR     = vec3 (1.0, 0.956, 0.621);
    const vec3  kYIQToG     = vec3 (1.0, -0.272, -0.647);
    const vec3  kYIQToB     = vec3 (1.0, -1.107, 1.704);

    float   YPrime  = dot (color, kRGBToYPrime);
    float   I       = dot (color, kRGBToI);
    float   Q       = dot (color, kRGBToQ);
    float   hue     = atan (Q, I);
    float   chroma  = sqrt (I * I + Q * Q);

    hue += hueAdjust;

    Q = chroma * sin (hue);
    I = chroma * cos (hue);

    vec3    yIQ   = vec3 (YPrime, I, Q);

    return vec3( dot (yIQ, kYIQToR), dot (yIQ, kYIQToG), dot (yIQ, kYIQToB) );

}

vec3 posterize(vec3 color){
  color = pow(color, vec3(gamma, gamma, gamma));
  color = color * numColors;
  color = floor(color);
  color = color / numColors;
  color = pow(color, vec3(1.0/gamma));
  return color;
};

vec4 cubic(float v){
    vec4 n = vec4(1.0, 2.0, 3.0, 4.0) - v;
    vec4 s = n * n * n;
    float x = s.x;
    float y = s.y - 4.0 * s.x;
    float z = s.z - 4.0 * s.y + 6.0 * s.x;
    float w = 6.0 - x - y - z;
    return vec4(x, y, z, w) * (1.0/6.0);
} 

uniform float exposure = 1;
uniform int samples = 10;

float warp = 1; // simulate curvature of CRT monitor
float scan = 1; // simulate darkness between scanlines

void main()
{
    vec2 coords = uvs;

    vec3 color;

    // squared distance from center

    vec2 dc = abs(0.5-coords);
    dc *= dc;
    
    // warp the fragment coordinates
    coords.x -= 0.5; coords.x *= 1.0+(dc.y*(0.3*warp)); coords.x += 0.5;
    coords.y -= 0.5; coords.y *= 1.0+(dc.x*(0.4*warp)); coords.y += 0.5;

    if (coords.y > 1.0 || coords.x < 0.0 || coords.x > 1.0 || coords.y < 0.0){
      discard;
    }

    color = texture(tex, coords).rgb;
    
    //vec3 colorBlur = texture(texBlur, coords).rgb;//

    //colorBlur = aces(colorBlur);//

    color *= exposure;

    color = hueShift(color, time);//

    color = posterize(color);

    color += mix(color,vec3(0.0),abs(sin((coords.y)*720)*0.5*scan));

    color.rgb = ((color.rgb - 0.5f) * max(1, 0)) + 0.5f;

    color = aces(color);
        
    fragColor = vec4(color, 1);
} 
