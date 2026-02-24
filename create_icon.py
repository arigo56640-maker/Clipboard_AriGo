"""יצירת אייקון לאפליקציה — script חד-פעמי."""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Background circle
        margin = max(1, size // 16)
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill="#7c3aed",
        )

        # Clipboard icon (simplified)
        cx, cy = size // 2, size // 2
        # Board
        bw = int(size * 0.5)
        bh = int(size * 0.6)
        bx = cx - bw // 2
        by = cy - bh // 2 + size // 10
        draw.rectangle([bx, by, bx + bw, by + bh], fill="#ffffff")

        # Clip at top
        cw = int(size * 0.25)
        ch = int(size * 0.12)
        clip_x = cx - cw // 2
        clip_y = by - ch // 2
        draw.rectangle([clip_x, clip_y, clip_x + cw, clip_y + ch], fill="#e0e0e0")

        # Text lines
        line_margin = int(size * 0.08)
        line_h = max(1, int(size * 0.05))
        line_w = int(bw * 0.6)
        for i in range(3):
            ly = by + int(bh * 0.3) + i * (line_h + line_margin)
            lx = bx + (bw - line_w) // 2
            if ly + line_h < by + bh - line_margin:
                draw.rectangle([lx, ly, lx + line_w, ly + line_h], fill="#7c3aed")

        images.append(img)

    # Save as .ico
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    ico_path = os.path.join(assets_dir, "icon.ico")

    # Use the largest as base, save all sizes
    images[-1].save(
        ico_path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=images[:-1],
    )
    print(f"Icon created: {ico_path}")


if __name__ == "__main__":
    create_icon()
