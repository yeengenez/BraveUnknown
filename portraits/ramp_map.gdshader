shader_type canvas_item;
// Colors a grayscale value map with a palette ramp (dark -> light).
// The part's red channel picks the position on the ramp; its alpha is kept.
uniform sampler2D ramp : filter_linear, repeat_disable;

void fragment() {
	vec4 part = texture(TEXTURE, UV);
	COLOR.rgb = texture(ramp, vec2(part.r, 0.5)).rgb;
}
