"""Generate PNG icon files for MobileTran APK"""
import struct
import zlib

def create_chunk(chunk_type, data):
    chunk = chunk_type + data
    crc = struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
    return struct.pack('>I', len(data)) + chunk + crc

def create_png(width, height, r, g, b):
    signature = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr = create_chunk(b'IHDR', ihdr_data)

    raw_data = bytearray()
    cx, cy = width // 2, height // 2
    for y in range(height):
        raw_data.append(0)  # filter byte
        for x in range(width):
            dx, dy = abs(x - cx), abs(y - cy)
            dist = (dx * dx + dy * dy) ** 0.5

            if dist < min(width, height) * 0.35:
                # T-shape logo area
                t_horiz = abs(y - cy) < height * 0.12
                t_vert = abs(x - cx) < width * 0.12 and x < cx + width * 0.25
                if t_horiz or t_vert:
                    raw_data.extend([255, 255, 255])  # white
                else:
                    raw_data.extend([r, g, b])
            elif dist < min(width, height) * 0.4:
                raw_data.extend([min(255, int(r * 1.2)), min(255, int(g * 1.2)), min(255, int(b * 1.2))])
            else:
                raw_data.extend([r, g, b])

    compressed = zlib.compress(bytes(raw_data))
    idat = create_chunk(b'IDAT', compressed)
    iend = create_chunk(b'IEND', b'')
    return signature + ihdr + idat + iend

# Generate icons
png_128 = create_png(128, 128, 26, 115, 232)
with open('icon.png', 'wb') as f:
    f.write(png_128)
print(f'icon.png: {len(png_128)} bytes (128x128)')

png_256 = create_png(256, 256, 26, 115, 232)
with open('icon_256.png', 'wb') as f:
    f.write(png_256)
print(f'icon_256.png: {len(png_256)} bytes (256x256)')