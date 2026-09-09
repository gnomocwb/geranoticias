import os
import struct
import zlib

def create_png(width, height, file_path):
    # RGBA image buffer
    raw_data = bytearray()
    
    # Rounded icon with sleek Cyan/Blue gradient
    cx = width / 2.0
    cy = height / 2.0
    radius = width * 0.44

    for y in range(height):
        raw_data.append(0)  # Filter byte: 0 (None)
        for x in range(width):
            dx = x - cx + 0.5
            dy = y - cy + 0.5
            dist = (dx * dx + dy * dy) ** 0.5

            if dist <= radius:
                # Vertical gradient from cyan (0, 210, 255) to deep blue (14, 90, 230)
                t = y / float(height)
                r = int(0 * (1 - t) + 14 * t)
                g = int(210 * (1 - t) + 110 * t)
                b = int(255 * (1 - t) + 245 * t)
                a = 255

                # Inner lightning bolt
                norm_x = (x - cx) / float(width)
                norm_y = (y - cy) / float(height)

                is_bolt = False
                if -0.28 <= norm_y < 0.02:
                    slope_x = 0.05 - (norm_y + 0.28) * 0.5
                    if abs(norm_x - slope_x) < 0.11:
                        is_bolt = True
                elif 0.02 <= norm_y <= 0.28:
                    slope_x = -0.05 - (norm_y - 0.02) * 0.5
                    if abs(norm_x - slope_x) < 0.11:
                        is_bolt = True

                if is_bolt:
                    r, g, b, a = 255, 255, 255, 255
                elif dist > radius - 1.2:
                    alpha_factor = max(0.0, min(1.0, radius - dist))
                    a = int(255 * alpha_factor)
            else:
                r, g, b, a = 0, 0, 0, 0

            raw_data.extend([r, g, b, a])

    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(c) & 0xffffffff)
        return struct.pack(">I", len(data)) + c + crc

    png_header = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    ihdr = chunk(b"IHDR", ihdr_data)
    idat = chunk(b"IDAT", zlib.compress(bytes(raw_data), 9))
    iend = chunk(b"IEND", b"")

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(png_header + ihdr + idat + iend)
    print(f"Generated {file_path} ({width}x{height})")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "..", "icons")
    for size in [16, 48, 128]:
        create_png(size, size, os.path.join(out_dir, f"icon-{size}.png"))
