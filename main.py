import struct
import os
import matplotlib.pyplot as plt
from collections import Counter

class BMPImage:
    def __init__(self, filepath):
        self.filepath = filepath
        self.read_header()

    def read_header(self):
        with open(self.filepath, 'rb') as f:
            self.header = f.read(14)

            self.type, self.size, self.reserved1, self.reserved2, self.offset = struct.unpack('<2sIHHI', self.header)

            # Read profile and color table information
            self.profile = f.read(self.offset - 14)
            self.color_table = f.read()

    def display_header(self):
        print(f'Type: {self.type.decode("utf-8")}')
        print(f'Size: {self.size}')
        print(f'Reserved1: {self.reserved1}')
        print(f'Reserved2: {self.reserved2}')
        print(f'Offset: {self.offset}')

        print('\nProfile:')
        for byte in self.profile:
            print(f'{byte:02X}', end=' ')

        print('\nColor Table:')
        for byte in self.color_table:
            print(f'{byte:02X}', end=' ')

    def plot_header(self):
        profile_counts = Counter(self.profile)
        color_table_counts = Counter(self.color_table)

        x_profile = profile_counts.keys()
        y_profile = profile_counts.values()

        x_color_table = color_table_counts.keys()
        y_color_table = color_table_counts.values()

        plt.figure(figsize=(12, 6))
        plt.bar(x_profile, y_profile)
        plt.xlabel('Byte Value')
        plt.ylabel('Frequency')
        plt.title('Profile')
        plt.show()

        plt.figure(figsize=(12, 6))
        plt.bar(x_color_table, y_color_table)
        plt.xlabel('Byte Value')
        plt.ylabel('Frequency')
        plt.title('Color Table')
        plt.show()

    def anonymize_header(self):
        self.reserved1 = 0
        self.reserved2 = 0
        with open(self.filepath, 'r+b') as f:
            f.seek(6)
            f.write(struct.pack('HH', self.reserved1, self.reserved2))

if __name__ == '__main__':
    bmp = BMPImage('test.bmp')
    bmp.display_header()
    bmp.plot_header()
    bmp.anonymize_header()
