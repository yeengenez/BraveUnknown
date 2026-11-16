shader_type canvas_item;
// Game-side addition (not part of the portrait module): recolours the pale
// cream cloth of an outfit to another colour, keeping gold trim and dark
// details. Used for the placeholder Mage outfit (cleric robe in violet).

uniform vec4 dark : source_color = vec4(0.16, 0.09, 0.27, 1.0);
uniform vec4 light : source_color = vec4(0.58, 0.44, 0.82, 1.0);

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	float hi = max(c.r, max(c.g, c.b));
	float lo = min(c.r, min(c.g, c.b));
	float sat = hi > 0.0 ? (hi - lo) / hi : 0.0;
	// pale, low-saturation pixels are the cloth
	float cloth = smoothstep(0.38, 0.22, sat) * smoothstep(0.45, 0.7, hi);
	float lum = dot(c.rgb, vec3(0.299, 0.587, 0.114));
	vec3 tinted = mix(dark.rgb, light.rgb, smoothstep(0.45, 1.0, lum));
	COLOR = vec4(mix(c.rgb, tinted, cloth), c.a);
}
