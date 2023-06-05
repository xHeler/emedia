import struct
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

class BMPImage:
    def __init__(self, filepath):
        self.filepath = filepath
        self._read_headers()
        self._read_dib_header()
        self._read_color_table_and_padding()

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

    def _read_color_table_and_padding(self):
        with open(self.filepath, "rb") as f:
            f.seek(self.offset)  # Move to color table / padding
            self.color_table_and_padding = f.read(self.offset - 14 - self.dib_header_size)

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

    def display_spectrum(self):
        img = Image.open(self.filepath).convert('L')  # Convert image to grayscale
        f = np.fft.fft2(img)  # Perform 2D FFT
        fshift = np.fft.fftshift(f)  # Shift the zero-frequency component to the center of the spectrum
        magnitude_spectrum = 20 * np.log(np.abs(fshift))  # Calculate the magnitude spectrum
        phase_spectrum = np.angle(fshift)  # Calculate the phase spectrum

        plt.figure(figsize=(14, 7))
        plt.subplot(121), plt.imshow(img, cmap='gray')
        plt.title('Input Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(122), plt.imshow(magnitude_spectrum, cmap='gray')
        plt.title('Magnitude Spectrum'), plt.xticks([]), plt.yticks([])
        
        # Add phase plot
        plt.figure(figsize=(7, 7))
        plt.imshow(phase_spectrum, cmap='gray')
        plt.title('Phase Spectrum'), plt.xticks([]), plt.yticks([])
        
        plt.show()
    
    def display_color_table(self):
        # Ensure color table exists (only for indexed images)
        if self.bit_count <= 8:
            with open(self.filepath, 'rb') as f:
                f.seek(self.offset)  # Move to color table
                self.color_table = f.read(4 * (2**self.bit_count))  # Each entry is 4 bytes

            # Unpack the color table entries
            self.color_table = [
                struct.unpack('<BBBx', self.color_table[i:i+4])
                for i in range(0, len(self.color_table), 4)
            ]

            # Print the color table
            for i, (r, g, b) in enumerate(self.color_table):
                print(f'Color {i}: R={r}, G={g}, B={b}')

            # Display color table
            fig, ax = plt.subplots(1, 1, figsize=(6, 2),
                                   tight_layout=True, 
                                   dpi=100)

            for sp in ax.spines.values():
                sp.set_visible(False)

            plt.xticks([])
            plt.yticks([])

            colors = [(r/255, g/255, b/255) for r, g, b in self.color_table]
            ax.imshow([colors], aspect='auto')
            plt.show()

        else:
            print('This image does not have a color table.')

    def display_padding(self):
        # Calculate row size without padding
        row_size_without_padding = self.width * self.bit_count // 8
        padding_size_per_row = (4 - row_size_without_padding % 4) % 4

        if padding_size_per_row == 0:
            print('This image does not have padding.')
            return

        with open(self.filepath, 'rb') as f:
            f.seek(self.offset)  # Move to the start of the pixel array
            for _ in range(self.height):
                f.read(row_size_without_padding)  # Skip the pixel data
                padding = f.read(padding_size_per_row)  # Read the padding
                print(padding)

    def anonymize_metadata(self):
        self.reserved1 = 0
        self.reserved2 = 0
        self.x_ppm = 0
        self.y_ppm = 0
        self.clr_used = 0
        self.clr_important = 0

        # Save the changes to the file
        with open(self.filepath, "rb+") as f:  # Update the mode to "rb+"
            # Write changes to reserved fields
            f.seek(6)  # reserved1 and reserved2 are located at 6 bytes into the file
            f.write(struct.pack("<HH", self.reserved1, self.reserved2))

            # Write changes to the DIB header
            f.seek(38)  # x_ppm and y_ppm are located at 38 bytes into the file
            f.write(struct.pack("<ii", self.x_ppm, self.y_ppm))
            f.seek(46)  # clr_used and clr_important are located at 46 bytes into the file
            f.write(struct.pack("<II", self.clr_used, self.clr_important))

    def anonymize_padding(self):
        padding_size = self.offset - 14 - self.dib_header_size
        with open(self.filepath, "rb+") as f:  # Update the mode to "rb+"
            f.seek(self.offset)  # Move to the start of the padding
            f.write(b'\0' * padding_size)  # Write zeroes over the padding

def main():
    bmp = BMPImage("test2.bmp")
    bmp.display_header()
    bmp.display_padding() 
    bmp.display_spectrum()
    bmp.display_color_table()
    bmp.anonymize_metadata()
    bmp.anonymize_padding()

if __name__ == "__main__":
    main()
