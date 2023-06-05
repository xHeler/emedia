import struct
from PIL import Image


class BMPImage:
    def __init__(self, filepath):
        self.filepath = filepath
        self._read_headers()
        self._read_dib_header()
        self._read_color_table()

    def _read_headers(self):
        with open(self.filepath, "rb") as f:
            self.header = f.read(14)
            (
                self.type,
                self.size,
                self.reserved1,
                self.reserved2,
                self.offset,
            ) = struct.unpack("<2sIHHI", self.header)

    def _read_dib_header(self):
        with open(self.filepath, "rb") as f:
            f.seek(14)  # Move to DIB header
            self.dib_header_size = struct.unpack("<I", f.read(4))[0]
            (
                self.width,
                self.height,
                self.planes,
                self.bit_count,
                self.compression,
                self.image_size,
                self.x_ppm,
                self.y_ppm,
                self.clr_used,
                self.clr_important,
            ) = struct.unpack("<iiHHIIiiII", f.read(self.dib_header_size - 4))

    def _read_color_table(self):
        with open(self.filepath, "rb") as f:
            f.seek(self.offset)  # Move to color table
            self.color_table = f.read()

    def display_header(self):
        print(f"Header (14 bytes):")
        print(f'Signature: {self.type.decode("utf-8")}')
        print(f"File Size (bytes): {self.size}")
        print(f"Reserved:")
        print(f"- reserved 1: {self.reserved1}")
        print(f"- reserved 2: {self.reserved2}")
        print(f"Data Offset: {self.offset}")
        print(f"\n\nInfo Header (40 bytes):")
        print(f"Size: {self.dib_header_size}")
        print(f"Width: {self.width}")
        print(f"Height: {self.height}")
        print(f"Planes: {self.planes}")
        print(f"Bit Count: {self.bit_count}")
        print(f"Compression: {self.compression}")
        print(f"Image Size: {self.image_size}")
        print(f"X Pixels Per Meter: {self.x_ppm}")
        print(f"Y Pixels Per Meter: {self.y_ppm}")
        print(f"Colors Used: {self.clr_used}")
        print(f"Important Colors: {self.clr_important}")

    def display_image(self):
        img = Image.open(self.filepath)
        img.show()

def main():
    bmp = BMPImage("test.bmp")
    bmp.display_header()
    bmp.display_image()


if __name__ == "__main__":
    main()
