from io import BytesIO
from PIL import Image
import numpy
import time
from random import randint

SAVE_KWARGS = {
#	'loop': 0,
	'save_all': True,
	'optimize': True,
	'duration': 85,
	'transparent': 0
}
COPY_FRAME_LIMIT = 75
GAMMA = 0
GAMMA_DIR = 1
GAMMA_MAX = 85
GAMMA_MIN = 0


def get_gamma() -> float:
	global GAMMA, GAMMA_DIR, GAMMA_MAX, GAMMA_MIN
	GAMMA = GAMMA + GAMMA_DIR * randint(0, 10)
	if GAMMA > GAMMA_MAX:
		GAMMA = GAMMA_MAX
		GAMMA_DIR = -1
		GAMMA_MAX = randint(35, 85)
	elif GAMMA < GAMMA_MIN:
		GAMMA = GAMMA_MIN
		GAMMA_DIR = 1
		GAMMA_MIN = randint(-25, 25)
	return GAMMA


class CubeFace():
	"""
	This class defines cube video creating and converting.
	"""

	@staticmethod
	def copy(face_filename: str, output_path: str,
					 frame_count: int, frame_duration: int) -> None:
		with Image.open(face_filename) as gif:
			if not gif.is_animated or not gif.n_frames > 1:
				raise ValueError('Source invalid')
			if frame_count > COPY_FRAME_LIMIT:
				frame_count = COPY_FRAME_LIMIT
			if frame_count > gif.n_frames:
				raise ValueError(
					'Requested frames (%d) out of range (%s)' % \
						(frame_count, gif.n_frames)
				)
			frame_start = randint(0, gif.n_frames - frame_count)
			image_list = []
			print('Ready to extract %d frames' % frame_count)
			for frame_index in range(frame_start, frame_start + frame_count):
				gif.seek(frame_index)
				image_list += [gif.copy()]
		print('Ready to write %d frames' % len(image_list))
		image_list[0].save(
			output_path, format='GIF', loop=0,
			append_images=image_list[1:], palette=Image.ADAPTIVE, **SAVE_KWARGS
		)
		print('Write %s: %d frames' % (output_path, len(image_list)))

	@staticmethod
	def write_capture(output_name: str, input, background_filename: str,
										cube_size: int, cube_color: tuple, pixel_size: int,
										image_count: int = 1000, do_mask: bool = False):
		import cv2
		capture = cv2.VideoCapture(input)
		if not capture.isOpened():
			raise ValueError('Input source unavailable (%s)' % capture)
		pixel_weight = int(256 // pixel_size * 1.1)
		if not do_mask:
			background = cv2.VideoCapture(background_filename)
			if not background.isOpened():
				raise ValueError(
					'Background source unavailable (%s)' % background_filename)
			cubed_size = cube_size // pixel_size
			else_color = (
				cube_color[0] // 2, cube_color[1] // 2, cube_color[2] // 2
			)
		else:
			cubed_size = cube_size // pixel_size
			else_color = (0, 0, 0)
		image_list = []
		while True:
			ret, frame = capture.read()
			if not ret:
				print('Input source read error (%s)' % caption)
				break
			if not do_mask:
				ret, bg_frame = background.read()
				if not ret:
					print('Background source read error (%s)' % background_filename)
					background = cv2.VideoCapture(background_filename)
					if not background.isOpened():
						raise ValueError(
							'Background source unavailable (%s)' % background_filename)
					ret, bg_frame = background.read()
					if not ret:
						print('Background source read error (%s)' % background_filename)
						break
				face = CubeFace.draw_face(
					cv2.resize(frame, (cubed_size, cubed_size)),
					cube_size, cube_color, pixel_size, pixel_weight, else_color
				)
				frame = cv2.addWeighted(face, 1.0, bg_frame, 0.5, 0.0)
				cv2.imshow(output_name, cv2.flip(frame, 1))
			else:
				face = CubeFace.draw_mask(
					cv2.resize(frame, (cubed_size, cubed_size)),
					cube_size, cube_color, pixel_size, pixel_weight, else_color
				)
				frame = face
				cv2.imshow(output_name, frame)
			image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
#			image_list += [image.convert(mode='P', palette=Image.ADAPTIVE)]
			image_list += [image]
			if cv2.waitKey(10) == 27 or len(image_list) == image_count:
				break
		cv2.destroyAllWindows()
		image_list[0].save(
			'%d-%s.gif' % (len(image_list), output_name), format='GIF', loop=0,
			append_images=image_list[1:], palette=Image.ADAPTIVE, **SAVE_KWARGS
		)
		print('Write %s: %d frames' % (output_name, len(image_list)))

	@staticmethod
	def show_capture(input, background_filename: str,
									 cube_size: int, cube_color: tuple, pixel_size: int,
									 do_mask: bool = False):
		import cv2
		capture = cv2.VideoCapture(input)
		if not capture.isOpened():
			raise ValueError('Input source unavailable (%s)' % capture)
		if not do_mask:
			background = cv2.VideoCapture(background_filename)
			if not background.isOpened():
				raise ValueError(
					'Background source unavailable (%s)' % background_filename)
			cubed_size = cube_size // pixel_size
			else_color = (
				cube_color[0] // 2, cube_color[1] // 2, cube_color[2] // 2
			)
		else:
			cubed_size = cube_size // pixel_size
			else_color = (0, 255, 0)
		pixel_weight = int(256 // pixel_size * 1.1)
		while True:
			ret, frame = capture.read()
			if not ret:
				print('Input source read error (%s)' % '')
				break
			if not do_mask:
				ret, bg_frame = background.read()
				if not ret:
					print('Background source read error (%s)' % background_filename)
					background = cv2.VideoCapture(background_filename)
					if not background.isOpened():
						raise ValueError(
							'Background source unavailable (%s)' % background_filename)
					ret, bg_frame = background.read()
					if not ret:
						print('Background source read error (%s)' % background_filename)
						break
				face = CubeFace.draw_face(
					cv2.resize(frame, (cubed_size, cubed_size)),
					cube_size, cube_color, pixel_size, pixel_weight, else_color
				)
				frame = cv2.addWeighted(face, 1.0, bg_frame, 0.5, 0.0)
				cv2.imshow('face', cv2.flip(frame, 1))
			else:
				face = CubeFace.draw_mask(
					cv2.resize(frame, (cubed_size, cubed_size)),
					cube_size, cube_color, pixel_size, pixel_weight, else_color
				)
				frame = face
				cv2.imshow('face', frame)
			if cv2.waitKey(10) == 27:
				break
		cv2.destroyAllWindows()

	@staticmethod
	def draw_face(frame, cube_size: int, cube_color: tuple,
								pixel_size: int, pixel_weight: int, else_color: tuple):
		import cv2
		face = numpy.full(
			(cube_size, cube_size, 3),
			(0, 0, 0), dtype=numpy.uint8
		)
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		half_pixel_size = pixel_size // 2
		x = half_pixel_size
		y = half_pixel_size
		for pixel in Image.fromarray(frame).getdata():
			width = pixel // pixel_weight
			if width > 1:
				half_width = width // 2
				else_width = width - half_width
				cv2.rectangle(
					face,
					(x - half_pixel_size, y - half_pixel_size),
					(x + half_pixel_size, y + half_pixel_size),
					else_color, -1
				)
				cv2.rectangle(
					face,
					(x - half_width, y - half_width),
					(x + else_width, y + half_width),
					cube_color, -1
				)
#			radius = pixel // pixel_weight
#			cv2.circle(face, (x, y), radius, cube_color, -1)
			x += pixel_size
			if x >= cube_size:
				x = half_pixel_size
				y += pixel_size
		return face

	@staticmethod
	def draw_mask(frame, cube_size: int, cube_color: tuple,
								pixel_size: int, pixel_weight: int, else_color: tuple):
		import cv2
		face = numpy.full(
			(cube_size, cube_size, 3),
			else_color, dtype=numpy.uint8
		)
#		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		half_pixel_size = pixel_size // 2
		x = half_pixel_size
		y = half_pixel_size
		for pixel in Image.fromarray(frame).getdata():
			width = (pixel[0] + pixel[1] + pixel[2]) // 3 // pixel_weight
			if width > 1:
				half_width = width // 2
				else_width = width - half_width
#				cv2.rectangle(
#					face,
#					(x - half_pixel_size, y - half_pixel_size),
#					(x + half_pixel_size, y + half_pixel_size),
#					pixel, -1
#				)
				cv2.rectangle(
					face,
					(x - half_width, y - half_width),
					(x + else_width, y + half_width),
					pixel, -1
				)
#			radius = pixel // pixel_weight
#			cv2.circle(face, (x, y), radius, cube_color, -1)
			x += pixel_size
			if x >= cube_size:
				x = half_pixel_size
				y += pixel_size
		return face

	@staticmethod
	def write_background(output_name: str, cube_size: int, cube_color: tuple,
											 pixel_size: int, border_size: int, do_cube: bool,
											 image_count: int = 1000):
		import cv2
		image_list = []
		frame = numpy.full(
			(cube_size, cube_size, 3),
			cube_color, dtype=numpy.uint8
		)
		last_frame = None
		while True:
			frame = CubeFace.draw_background(
				frame, cube_size, cube_color, pixel_size, border_size
			)
			if do_cube:
				cube_frame = CubeFace.cube_background(frame, cube_size)
				frame = cv2.addWeighted(frame, 0.5, cube_frame, 0.5, get_gamma())
#				if last_frame is not None:
#					sub_frame = cv2.addWeighted(frame, 0.5, last_frame, 0.6, 0.0)
#					image = Image.fromarray(cv2.cvtColor(sub_frame, cv2.COLOR_BGR2RGB))
#					image_list += [image.convert(mode='P', palette=Image.ADAPTIVE)]
#					cv2.imshow(output_name, sub_frame)
#					if cv2.waitKey(10) == 27 or len(image_list) >= image_count:
#						break
#				last_frame = cube_frame
			image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
			image_list += [image.convert(mode='P', palette=Image.ADAPTIVE)]
			cv2.imshow(output_name, frame)
			if cv2.waitKey(10) == 27 or len(image_list) >= image_count:
				break
		cv2.destroyAllWindows()
		image_list[0].save(
			'%d-%s.gif' % (len(image_list), output_name), format='GIF', loop=0,
			append_images=image_list[1:], palette=Image.ADAPTIVE, **SAVE_KWARGS
		)
		print('Write %s: %d frames' % (output_name, len(image_list)))

	@staticmethod
	def show_background(cube_size: int, cube_color: tuple,
											pixel_size: int, border_size: int, do_cube: bool):
		import cv2
		frame = numpy.full(
			(cube_size, cube_size, 3),
			cube_color, dtype=numpy.uint8
		)
		last_frame = None
		while True:
			frame = CubeFace.draw_background(
				frame, cube_size, cube_color, pixel_size, border_size
			)
			if do_cube:
				cube_frame = CubeFace.cube_background(frame, cube_size)
				frame = cv2.addWeighted(frame, 0.5, cube_frame, 0.5, get_gamma())
#				if last_frame is not None:
#					sub_frame = cv2.addWeighted(frame, 0.6, last_frame, 0.6, 0)
#					cv2.imshow('background', sub_frame)
#					if cv2.waitKey(75) == 27:
#						break
#				last_frame = cube_frame
			cv2.imshow('background', frame)
			if cv2.waitKey(75) == 27:
				break
		cv2.destroyAllWindows()

	@staticmethod
	def draw_background(frame, cube_size: int, cube_color: tuple,
											pixel_size: int, border_size: int):
		import cv2
		light = 0
		light_limit = 50
		for x in range(0, cube_size, pixel_size):
			for y in range(0, cube_size, pixel_size):
				if randint(0, 10) > 5:
					light = randint(0, light_limit)
				else:
					light += randint(0, 10)
				if light > light_limit:
					light = 0
				color = (
					cube_color[0] + light,
					cube_color[1] + light,
					cube_color[2] + light
				)
				cv2.rectangle(
					frame, (x, y), (x + pixel_size, y + pixel_size),
					color, -1
				)
#				color = (
#					color[0] + light,
#					color[1] + light,
#					color[2] + light
#				)
				color = cube_color
				cv2.rectangle(
					frame, (x, y), (x + pixel_size, y + pixel_size),
					color, border_size
				)
		return frame

	@staticmethod
	def cube_background(frame, cube_size: int):
		import cv2
		# Source rectangle background
		tl0 = [0, 0]
		tr0 = [cube_size - 1, 0]
		bl0 = [0, cube_size - 1]
		br0 = [cube_size - 1, cube_size - 1]
		rect = numpy.array([tl0, tr0, bl0, br0], dtype='float32')
		# Transform point's coordinates
		side_25 = cube_size // 5
		side_75 = cube_size - side_25 - 1
		tl5 = [side_75, side_25]
		tr5 = [side_25, side_25]
		bl5 = [side_75, side_75]
		br5 = [side_25, side_75]
		# Side left
		dest = numpy.array([tl5, tr0, bl5, br0], dtype='float32')
		M = cv2.getPerspectiveTransform(rect, dest)
		side_l = cv2.warpPerspective(frame, M, (cube_size, cube_size))
		# Side right
		dest = numpy.array([tl0, tr5, bl0, br5], dtype='float32')
		M = cv2.getPerspectiveTransform(rect, dest)
		side_r = cv2.warpPerspective(frame, M, (cube_size, cube_size))
		# Side bottom
		dest = numpy.array([tl5, tr5, bl0, br0], dtype='float32')
		M = cv2.getPerspectiveTransform(rect, dest)
		side_b = cv2.warpPerspective(frame, M, (cube_size, cube_size))
		# Side top
		dest = numpy.array([tl0, tr0, bl5, br5], dtype='float32')
		M = cv2.getPerspectiveTransform(rect, dest)
		side_t = cv2.warpPerspective(frame, M, (cube_size, cube_size))
		# Side back
		tl5 = [side_75 - 1, side_25 + 1]
		tr5 = [side_25 + 1, side_25 + 1]
		bl5 = [side_75 - 1, side_75 - 1]
		br5 = [side_25 + 1, side_75 - 1]
		dest = numpy.array([tl5, tr5, bl5, br5], dtype='float32')
		M = cv2.getPerspectiveTransform(rect, dest)
		side_back = cv2.warpPerspective(frame, M, (cube_size, cube_size))
		# Merge sides
		side_h = cv2.addWeighted(side_t, 1.0, side_b, 1.0, 0.0)
		side_v = cv2.addWeighted(side_l, 1.0, side_r, 1.0, 0.0)
		sides = cv2.addWeighted(side_h, 1.0, side_v, 1.0, 0.0)
		return cv2.addWeighted(sides, 1.0, side_back, 1.0, 0.0)

	@staticmethod
	def convert(input, output_path: str, frame_count: int) -> None:
		import cv2
		capture = cv2.VideoCapture(input)
		if not capture.isOpened():
			raise ValueError('Input source unavailable (%s)' % capture)
		image_list = []
		while True:
			ret, frame = capture.read()
			if not ret:
				print('Input source read error (%s)' % caption)
				break
			image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
			image_list += [image.convert(mode='P', palette=Image.ADAPTIVE)]
			cv2.imshow(output_path, frame)
			if cv2.waitKey(10) == 27 or len(image_list) == frame_count:
				break
		cv2.destroyAllWindows()
		image_list[0].save(
			output_path, format='GIF', loop=0,
			append_images=image_list[1:], palette=Image.ADAPTIVE, **SAVE_KWARGS
		)
		print('Write %s: %d frames' % (output_name, len(image_list)))


if __name__ == '__main__':
	dark_titan_color = (135, 120, 125)
	pixel_size = 18
	border_size = 3
	cube_size = pixel_size * 36
	choice = 5
	if choice == 0:
		CubeFace.copy('1000-face.gif', '100-face.gif', 100, 150)
	elif choice == 1:
		CubeFace.show_background(
			cube_size, dark_titan_color,
			pixel_size, border_size,
			do_cube=True
		)
	elif choice == 2:
		CubeFace.write_background(
			'background',
			cube_size, dark_titan_color,
			pixel_size, border_size,
			do_cube=True, image_count=50
		)
	elif choice == 3:
		CubeFace.show_capture(
			0, '50-background.gif',
			cube_size, dark_titan_color, pixel_size // 2
		)
	elif choice == 4:
		CubeFace.write_capture(
			'face', 0, '50-background.gif',
			cube_size, dark_titan_color, pixel_size // 2, image_count=75
		)
	elif choice == 5:
		CubeFace.convert(
			'/home/rt/Downloads/new-face.mp4', 'new_face.gif', 1000
		)
	elif choice == 6:
		CubeFace.show_capture(
			'/home/rt/Downloads/woman.mp4', '100-background.gif',
			cube_size, dark_titan_color, pixel_size // 2
		)
	elif choice == 7:
		CubeFace.show_capture(
			0, '100-background.gif',
			cube_size, dark_titan_color, pixel_size // 4, do_mask=True
		)
	elif choice == 8:
		CubeFace.write_capture(
			'face', 0, '50-background.gif',
			cube_size, dark_titan_color, pixel_size // 4, image_count=300,
			do_mask=True
		)
# <video loop="" autoplay="" width="100%" height="100%">
#  <source type="video/mp4" src="/gallery/soundfile/catalog/image/proba_1.mp4/">
#  Your browser does not support the video tag.
# </video>
