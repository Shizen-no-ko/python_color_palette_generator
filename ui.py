from tkinter import *
from PIL import ImageTk, Image
from tkinter.filedialog import askopenfilenames
import numpy as np
from matplotlib.colors import rgb2hex
import pyperclip


class UI:

	def __init__(self):
		self.window = Tk()
		self.window.title("Image Palette Finder")
		self.window.configure(bg="#fa7d09")
		self.headerFont = ("Helvetica", 28, "bold")
		self.buttonFont = ("Helvetica", 15, "bold")
		self.colorNameFont = ("Helvetica", 10, "bold")
		self.pic_size = (300, 300)
		self.button = []
		self.ui()
		self.window.mainloop()

	def ui(self):
		self.header = Label(self.window, width=28, font=self.headerFont, text="Image Palette Finder", bg="#fa7d09",
		                    fg="#4a3f35", pady=10)
		self.get_image_button = Button(self.window, text="Select Image", font=self.buttonFont, fg="#fa7d09",
		                               bg="#4a3f35", activebackground="#fa7d09", activeforeground="#4a3f35",
		                               relief=FLAT, command=self.select)
		self.canvas = Canvas(self.window, width=300, height=300, bg="#fa7d09", highlightthickness=0)
		self.image_on_canvas = self.canvas.create_image(150, 150)
		self.header.grid(column=0, row=0, columnspan=4, pady=10)
		self.get_image_button.grid(column=4, row=0, pady=10)
		self.canvas.grid(column=2, row=1, pady=10, rowspan=10)
		self.color_buttons()

	def color_buttons(self):
		# initial creation and layout of color buttons
		for i in range(10):
			self.button.append(
				Button(self.window, text='#' + str(i + 1), command=lambda i=i: self.copy_clipboard(i + 1),
				       font=self.buttonFont, fg="#fa7d09",
				       bg="#4a3f35", activebackground="#fa7d09", activeforeground="#4a3f35",
				       relief=FLAT, width=20))
			if i % 2 == 0:
				self.button[i].grid(column=3, row=i + 1)
			else:
				self.button[i].grid(column=4, row=i + 0, padx=10)

	def update_color_buttons(self):
		for i in range(10):
			# sets color to each button and text to hex_code and passes
			# unique hex code for the command of each button
			self.button[i].config(bg=self.hex_codes[i], fg=self.complimentary_codes[i], text=self.hex_codes[i],
			                      command=lambda i=i: self.copy_clipboard(self.hex_codes[i]))

	@staticmethod
	def copy_clipboard(text):
		# copies hex code to clipboard
		pyperclip.copy(text)

	def select(self):
		# dialog to open image
		self.input_filename = askopenfilenames(title='select', filetypes=[
			("image", ".jpeg"),
			("image", ".png"),
			("image", ".jpg"),
		])[0]
		# open image with pillow
		self.full_image = Image.open(self.input_filename)
		# print(self.full_image)
		# convert to RGB
		self.full_image.convert("RGB")
		# print(self.full_image)
		# copy image for conversion to thumbnail
		self.thumbnail_img = self.full_image
		# convert to thumbnail
		self.thumbnail_img.thumbnail(self.pic_size, Image.ANTIALIAS)
		# set and display image on canvas
		self.display_img = ImageTk.PhotoImage(self.thumbnail_img)
		self.canvas.itemconfig(self.image_on_canvas, image=self.display_img, anchor=CENTER)
		self.do_the_magic()

	def do_the_magic(self):
		# convert image to numpy array
		self.convert_to_numpy()
		# get the unique color values
		self.get_unique()
		# create top 10 list with occurrence counts and their indexes
		self.group_lists()
		# get list of hex codes from the top 10 list
		self.get_colors()
		# update the color buttons color and text and command
		self.update_color_buttons()

	def convert_to_numpy(self):
		# convert image to numpy array
		self.image_numpy = np.asarray(self.full_image, dtype="int32")
		# print(self.image_numpy)
		self.image_numpy = np.divide(self.image_numpy, 255)
		self.image_numpy = np.around(self.image_numpy, decimals=1)
		#print(self.image_numpy)

	def get_unique(self):
		# extract list of unique colors and the amount of each
		unique, count = np.unique(self.image_numpy.reshape(-1, self.image_numpy.shape[2]), axis=0, return_counts=True)
		self.unique = unique
		self.count = count

	def group_lists(self):
		# create top 10 list with occurrence counts and their indexes
		self.pairs = []
		for i in range(len(self.count)):
			# create list of occurrence counts paired with index
			self.pairs.append((self.count[i], i))
		# sort by index
		self.pairs.sort(key=lambda pair: pair[0])
		# print(self.pairs[-10:][::-1])
		# get indexes of 10 largest occurrences
		self.indices = [b for (a, b) in self.pairs[-10:][::-1]]
		# print(self.indices)

	def get_colors(self):
		# use top 10 index list to generate rgb list from self.unique list
		self.rgb = []
		for index in self.indices:
			self.rgb.append(self.unique[index])
		# convert float values to hex codes
		self.hex_codes = []
		self.complimentary_codes = []
		for color in self.rgb:
			hex_version = rgb2hex(color)
			self.hex_codes.append(hex_version)
			self.complimentary_codes.append(self.get_complementary(hex_version))

	def get_complementary(self, color):
		# strip the # from the beginning
		color = color[1:]
		# convert the string into hex
		color = int(color, 16)
		# invert the three bytes
		# as good as subtracting each of RGB component by 255(FF)
		comp_color = 0xFFFFFF ^ color
		# convert the color back to hex by prefixing a #
		comp_color = "#%06X" % comp_color
		# return the result
		return comp_color
