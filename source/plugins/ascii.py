from PIL import Image
import cv2
import imutils
import numpy


def convert_capture(source, width, color, invert, output) -> None:
	"""
	"""
	print('Starting...')
	frame_list = []
	cap = cv2.VideoCapture(source)
	try:
		while True:
			ret, frame = cap.read()
			if not ret:
				break
			result = convert_frame(frame, width, color, invert)
			cv2.imshow(str(source), frame)
			cv2.imshow('result', result)
			if cv2.waitKey(1) == 27:
				break
			frame_list += [Image.fromarray(result)]
	except KeyboardInterrupt:
		print('Interrupting...')
	except Exception as exc:
		print(exc.message)
	im = frame_list[0]
	im.save(
		output, format='GIF', append_images=frame_list,
		save_all=True, duration=100, loop=1, transparency=0
	)


def convert_frame(frame, width, color, invert) -> list:
	"""
	"""
	scale = 10
	frame_height, frame_width = frame.shape[:2]
	height = width * frame_height // frame_width
	frame = imutils.resize(frame, width=width // scale, height=height // scale)
	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	frame = cv2.flip(frame, 1)
	if invert:
		frame = cv2.bitwise_not(frame)
	frame = Image.fromarray(frame)
	d_value = 255 // scale * 2
	pixels = []
	for pixel in frame.getdata():
		pixels += [pixel // d_value];
	result = numpy.zeros((int(height), int(width), 4), dtype=numpy.uint8)
	y = scale // 2
	for i in range(0, len(pixels), frame.width):
		x = scale // 2
		for pixel in pixels[i: i + frame.width]:
			if pixel > 1:
				cv2.circle(result, (x, y), pixel, color, -1)
			x += scale
		y += scale
	return result


if __name__ == '__main__':
	convert_capture(0, 1024, (200, 255, 180, 200), False, 'sample.gif')

