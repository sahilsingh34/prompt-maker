"""
Generate the PromptEnhancer app icon (icon.ico).

Creates a modern gradient icon with a lightning bolt / sparkle design.
Saves multiple sizes (16, 32, 48, 64, 128, 256) in a single .ico file.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont


def create_icon(output_path: str):
    """Generate the PromptEnhancer icon."""
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Gradient background (rounded rectangle)
        # Deep indigo to purple gradient approximation
        padding = max(1, size // 16)
        
        # Draw gradient background using layered rectangles
        for y in range(padding, size - padding):
            ratio = y / size
            r = int(79 + (139 - 79) * ratio)   # 79 → 139
            g = int(70 + (92 - 70) * ratio)     # 70 → 92
            b = int(229 + (246 - 229) * ratio)  # 229 → 246
            draw.line([(padding, y), (size - padding, y)], fill=(r, g, b, 255))

        # Round the corners by masking
        mask = Image.new("L", (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        radius = max(2, size // 5)
        mask_draw.rounded_rectangle(
            [padding, padding, size - padding, size - padding],
            radius=radius,
            fill=255,
        )
        img.putalpha(mask)

        # Draw lightning bolt / sparkle
        cx, cy = size // 2, size // 2
        
        if size >= 48:
            # Draw a stylized lightning bolt
            bolt_scale = size / 256.0
            
            # Lightning bolt points (relative to center)
            points = [
                (cx - int(25 * bolt_scale), cy - int(55 * bolt_scale)),
                (cx + int(15 * bolt_scale), cy - int(10 * bolt_scale)),
                (cx - int(5 * bolt_scale), cy - int(10 * bolt_scale)),
                (cx + int(25 * bolt_scale), cy + int(55 * bolt_scale)),
                (cx - int(15 * bolt_scale), cy + int(10 * bolt_scale)),
                (cx + int(5 * bolt_scale), cy + int(10 * bolt_scale)),
            ]
            draw.polygon(points, fill=(255, 255, 255, 240))

            # Add sparkle dots
            sparkle_r = max(1, int(4 * bolt_scale))
            sparkle_positions = [
                (cx + int(35 * bolt_scale), cy - int(35 * bolt_scale)),
                (cx - int(40 * bolt_scale), cy + int(30 * bolt_scale)),
                (cx + int(40 * bolt_scale), cy + int(25 * bolt_scale)),
            ]
            for sx, sy in sparkle_positions:
                draw.ellipse(
                    [sx - sparkle_r, sy - sparkle_r, sx + sparkle_r, sy + sparkle_r],
                    fill=(255, 220, 100, 200),
                )
        elif size >= 32:
            # Simplified bolt for small sizes
            bolt_scale = size / 256.0 * 2.5
            points = [
                (cx - int(10 * bolt_scale), cy - int(20 * bolt_scale)),
                (cx + int(6 * bolt_scale), cy - int(3 * bolt_scale)),
                (cx - int(2 * bolt_scale), cy - int(3 * bolt_scale)),
                (cx + int(10 * bolt_scale), cy + int(20 * bolt_scale)),
                (cx - int(6 * bolt_scale), cy + int(3 * bolt_scale)),
                (cx + int(2 * bolt_scale), cy + int(3 * bolt_scale)),
            ]
            draw.polygon(points, fill=(255, 255, 255, 240))
        else:
            # Very small: just a white bolt shape or "⚡"
            try:
                font = ImageFont.truetype("seguiemj.ttf", max(8, size - 6))
                draw.text((padding + 1, padding), "⚡", fill=(255, 255, 255), font=font)
            except Exception:
                # Fallback: simple diamond shape
                s = size // 4
                draw.polygon(
                    [(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)],
                    fill=(255, 255, 255, 240),
                )

        images.append(img)

    # Save as .ico with all sizes
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    images[-1].save(
        output_path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=images[:-1],
    )
    print(f"Icon saved to: {output_path}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    icon_path = os.path.join(project_dir, "assets", "icon.ico")
    create_icon(icon_path)
