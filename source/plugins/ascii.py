from PIL import Image

#ASCII_CHARS = [' ', '⬝', '·', '•']
ASCII_CHARS = [' ', ' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']

D_VALUE = 256 // len(ASCII_CHARS) + 1


def convert(filepath: str, width: int, aspect: float,
						white_background: bool = False):
	char_list = list(reversed(ASCII_CHARS)) \
		if white_background else ASCII_CHARS
	image = Image.open(filepath)
	# Resize image
	iw, ih = image.size
	height = int(width * ih / iw / aspect)
	image = image.resize((width, height))
	# Convert image to greyscale and define chars
	greyscale_image = image.convert('L')
	ascii_str = ""
	for pixel in greyscale_image.getdata():
		ascii_str += char_list[pixel//D_VALUE];
	# Form string lines from chars
	ascii_img = []
	for i in range(0, len(ascii_str), greyscale_image.width):
		ascii_img += [ascii_str[i: i + greyscale_image.width]]
	return ascii_img
#	with open(filepath + ".txt", "w") as file:
#		file.write(ascii_img);


if __name__ == '__main__':
	filepath = '/home/rt/Downloads/face.png'
	ascii_img = convert(filepath, 24, 2.2, False)
	with open(filepath + ".txt", "w") as file:
		file.write('\n'.join(ascii_img));
