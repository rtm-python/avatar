from io import BytesIO
from PIL import Image
from PIL import ImageSequence
import imutils
import numpy
import cv2
import time


class BubbleVideo():
	"""
	This class defines bubble video creating and converting.
	"""
	save_kwargs = {
		'save_all': True,
		'duration': 85,
#		'transparency': 0,
#		'background': 0,
		'optimize': True
#		'loop': 0
	}
	extra_ratio = 1.25
	capture = None
	input = None
	video = None
	video_width = None
	video_height = None
	bubble_size = None
	bubble_ratio = None
	bubble_color = None
	bubbled_width = None
	bubbled_height = None
	background = None
	background_color = None

	def __init__(self, input, background = None, background_color = None,
							 frame_duration = None) -> "BubbleVideo":
		"""
		Initiate object with input source.
		"""
		self.input = str(input)
		self.capture = cv2.VideoCapture(input)
		if not self.capture.isOpened():
			raise ValueError('Input source unavailable (%s)' % input)
		if background:
			self.background = cv2.VideoCapture(background)
			if not self.background.isOpened():
				raise ValueError('Background source unavailable (%s)' % background)
		elif background_color:
			self.background_color = background_color
		else:
			self.background_color = (0, 0, 0)
		if frame_duration:
			self.save_kwargs['duration'] = frame_duration

	def convert2video(self, output, width,
										bubble_size, bubble_color, mirrored_preview) -> None:
		"""
		Convert capture to bubble video and output video file.
		ffmpeg -i video.mp4 -i audio.mp3 -c copy -map 0:v -map 1:a -shortest output.mp4
		"""
		ret, frame = self.capture.read()
		bg_ret, bg_frame = self.background.read() \
			if self.background is not None else (True, None)
		if not ret or not bg_ret:
			raise ValueError('Capture read nothing')
		frame_height, frame_width = frame.shape[:2]
		self.video_width = width
		self.video_height = int(width * frame_height // frame_width)
		fourcc = cv2.VideoWriter_fourcc(*'MJPG')
		self.video = cv2.VideoWriter(
			output, fourcc, 20.0,	(self.video_width, self.video_height)
		)
		self.bubble_size = bubble_size
		self.bubble_ratio = int(255 // bubble_size * self.extra_ratio)
		self.bubble_color = bubble_color
		self.bubbled_width = self.video_width // bubble_size
		self.bubbled_height = self.video_height // bubble_size
		try:
			while True:
				ret, frame = self.capture.read()
				bg_ret, bg_frame = self.background.read() \
					if self.background is not None else (True, None)
				if not ret or not bg_ret:
					print('Capture read nothing')
					break
				bubble_frame = self.bubble_frame(frame, bg_frame)
				self.video.write(bubble_frame)
				if mirrored_preview:
					bubble_frame = cv2.flip(bubble_frame, 1)
				cv2.imshow(self.input, cv2.cvtColor(bubble_frame, cv2.COLOR_RGB2BGR))
				if cv2.waitKey(1) == 27:
					break
		except KeyboardInterrupt:
			pass
		except Exception as exc:
			print(exc)

	def convert2gif(self, output, width,
									bubble_size, bubble_color, mirrored_preview) -> None:
		"""
		Convert capture to bubble video and output gif file.
		"""
		ret, frame = self.capture.read()
		bg_ret, bg_frame = self.background.read() \
			if self.background is not None else (True, None)
		if not ret or not bg_ret:
			raise ValueError('Capture read nothing')
		frame_height, frame_width = frame.shape[:2]
		self.video_width = width
		self.video_height = int(width * frame_height // frame_width)
		self.bubble_size = bubble_size
		self.bubble_ratio = int(255 // bubble_size * self.extra_ratio)
		self.bubble_color = bubble_color
		self.bubbled_width = self.video_width // bubble_size
		self.bubbled_height = self.video_height // bubble_size
#		bytes_list = []
		image_list = []
		image_palette = Image.ADAPTIVE
		try:
			while True:
				ret, frame = self.capture.read()
				bg_ret, bg_frame = self.background.read() \
					if self.background is not None else (True, None)
				if not ret or not bg_ret:
					print('Capture read nothing')
					break
				bubble_frame = self.bubble_frame(frame, bg_frame)
				image_list += [
					Image.fromarray(bubble_frame).convert(
						mode='P', palette=image_palette
					)
				]
#				bytes_list += [
#					BytesIO()
#				]
#				image_list[-1].save(bytes_list[-1], format='GIF')
#				bytes_list[-1] = Image.open(bytes_list[-1])
				if mirrored_preview:
					bubble_frame = cv2.flip(bubble_frame, 1)
				cv2.imshow(self.input, cv2.cvtColor(bubble_frame, cv2.COLOR_RGB2BGR))
				if cv2.waitKey(1) == 27:
					break
		except KeyboardInterrupt:
			pass
		except Exception as exc:
			print(exc)
		temp = time.time()
		image_list[0].save(
			'%d-%s' % (len(image_list), output),
			format='GIF', append_images=image_list[1:],
			palette=image_palette, **self.save_kwargs
		)
		print('image_list.save() elapsed %s' % (time.time() - temp))
#		temp = time.time()
#		bytes_list[0].save(
#			'gif_%s' % output, append_images=bytes_list[1:],
#			palette=image_palette, **self.save_kwargs
#		)
#		print('bytes_list.save() elapsed %s' % (time.time() - temp))

	def bubble_frame(self, frame, bg_frame) -> object:
		"""
		Convert frame to bubbles.
		"""
		frame = imutils.resize(
			frame, width=self.bubbled_width, height=self.bubbled_height
		)
		if bg_frame is not None:
			result = imutils.resize(
				bg_frame, width=self.video_width, height=self.video_height
			)
		else:
			result = numpy.full(
				(self.video_height, self.video_width, 3),
				self.background_color, dtype=numpy.uint8
			)
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		frame = Image.fromarray(frame)
		x_in_row = 0
		x, y = (self.bubble_size // 2, self.bubble_size // 2)
		for pixel in frame.getdata():
			radius = pixel / self.bubble_ratio
			if radius > self.extra_ratio * 2:
				cv2.circle(
					result, (x, y), int(radius * self.extra_ratio),
					self.bubble_color, -1
				)
			x += self.bubble_size
			x_in_row += 1
			if x_in_row == self.bubbled_width:
				x_in_row = 0
				y += self.bubble_size
				x = self.bubble_size // 2
		return result

	def release(self) -> None:
		"""
		Release objects.
		"""
		if self.capture:
			self.capture.release()
		if self.background:
			self.background.release()
		if self.video:
			self.video.release()
		cv2.destroyAllWindows()

	@staticmethod
	def copy_gif(source, target,
							 frame_start, frame_count, frame_duration) -> None:
		"""
		Copy frames from gif-source file to gif-tagret file
		with starting point and frames count.
		"""
		gif = Image.open(source)
		if not gif.is_animated or not gif.n_frames > 1:
			raise ValueError('Source invalid')
		if frame_start < 0 or frame_start + frame_count > gif.n_frames:
			raise ValueError(
				'Requested frames (%d) out of range (%s)' % \
					(frame_start + frame_count, gif.n_frames)
			)
		image_list = []
		image_palette = Image.ADAPTIVE
		for index, frame in enumerate(ImageSequence.Iterator(gif)):
			if index >= frame_start + frame_count:
				break
			if index >= frame_start:
				image_list += [frame.copy()]
		save_kwargs = {
			'save_all': True,
			'duration': frame_duration,
#			'transparency': 0,
#			'background': 0,
			'optimize': True
#			'loop': 0
		}
		temp = time.time()
		image_list[0].save(
			target, format='GIF', append_images=image_list[1:],
			palette=image_palette, **save_kwargs
		)
		print('image_list.save() elapsed %s' % (time.time() - temp))


if __name__ == '__main__':
	if True:
		rgb_background = (50, 25, 0)
		rgb_color = (255, 255, 150)
		bubble_video = BubbleVideo(
			0, background_color=rgb_background, frame_duration=1
		)
		bubble_video.convert2gif('video.gif', 640, 10, rgb_color, True)
#		bubble_video.convert2video('video.mp4', 640, 10, (235, 255, 215), True)
		bubble_video.release()
#	BubbleVideo.copy_gif('422-video.gif', 'copy.gif', 50, 200, 85)
