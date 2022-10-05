#!/usr/bin/env python3

import sys
import math
import base64
import tkinter

from io import BytesIO
from PIL import Image as PILImage

## NO ADDITIONAL IMPORTS ALLOWED!

class Image:
    def __init__(self, width, height, pixels):
        self.width = width
        # Width of the image in pixels
        self.height = height
        # Height of the image in pixels
        self.pixels = pixels
        # A list of pixel values (0 - 255) stored in row-major order
        
    def get_pixel(self, x, y):
        '''
        Return the pixel value of the picture at the position (x, y)
        '''
        return self.pixels[y * self.width + x]
    
    def get_pixel_extended(self, x, y):
        '''
        Returns the pixel value in the given position (x, y).
        If the position is out of range, returns closest valid pixel value.
        '''
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x > self.width - 1:
            x = self.width - 1
        if y > self.height - 1:
            y = self.height - 1
        
        return self.get_pixel(x, y)
    
    def set_pixel(self, x, y, c):
        '''
        Set the pixel of the image at the position (x, y) to the c
        '''
        self.pixels[y * self.width + x] = c

    def apply_per_pixel(self, func):
        '''
        Apply function 'func' to every pixel value of the image
        '''
        result = Image.new(self.width, self.height)
        for y in range(result.height):
            for x in range(result.width):
                color = self.get_pixel(x, y)
                newcolor = func(color)
                result.set_pixel(x, y, newcolor)
        return result

    def inverted(self):
        return self.apply_per_pixel(lambda c: 255-c)
    
    def clip(self):
        for i in range(len(self.pixels)):
            self.pixels[i] = int(round(self.pixels[i]))
            if self.pixels[i] > 255:
                self.pixels[i] = 255
            if self.pixels[i] < 0:
                self.pixels[i] = 0         
                
    def correlation(self, kernel):
        #Create a copy of the image
        result = Image.new(self.width, self.height)
        
        #Calculate the distance 
        size = len(kernel) // 2
        
        #Apply kernel to every pixel
        for y in range(result.height):
            for x in range(result.width):
                new_value = 0
                y1 = -1
                for j in range(y-size,y+size+1):
                    y1 += 1 
                    x1 = -1
                    for i in range(x-size,x+size+1):
                        x1 += 1
                        new_value += self.get_pixel_extended(i, j) * kernel[y1][x1]
                result.set_pixel(x, y, new_value)
        return result
                
    def blurred(self, n):
        kernel = [[1/n**2 for i in range(n)] for i in range(n)]
        result = self.correlation(kernel)
        result.clip()
        return result
        
    def sharpened(self, n):
        kernel = [[0 - 1/n**2 for i in range(n)] for i in range(n)]
        kernel[n//2][n//2] += 2
        result = self.correlation(kernel)
        result.clip()
        return result

    def edges(self):
        kernel_x = [[-1, 0, 1],[-2, 0, 2],[-1, 0, 1]]
        kernel_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
        result1 = self.correlation(kernel_x)
        result2 = self.correlation(kernel_y)
        result = Image.new(self.width, self.height)
        for i in range(len(result.pixels)):
            result.pixels[i] = math.sqrt(result1.pixels[i]**2 + result2.pixels[i]**2)
        result.clip()
        return result
    
    def normalization(self):
        '''
        Returns a image that each of it's pixel values are scaled linearly such that darkest pixel in the
        output has a pixel value of 0 and brightest pixel has a pixel value of 255
        '''
        #Create new copy of the input image
        result = Image.new(self.width, self.height)
        values = []
        #Copy each pixel value that will be scaled linearly
        for y in range(self.height):
            for x in range(self.width):
                values.append(self.get_pixel(x,y))
        min_value = min(values)
        step = 255/(max(values) - min_value)
        #Apply linear scale to each pixel values --> new_value = (value - min_value) * (new_max - new_min)/(max_value-min_value)
        #And set this value as pixel of the new image at the position (x,y)
        for y in range(result.height):
            for x in range(result.width):
                new_value = (values[y*result.width + x] - min_value) * step
                result.set_pixel(x, y, new_value)
        result.clip()
        return result
    
    def gaussian_filter(self):
        '''
        Returns an image that is blurred by using a sigma value which is choosed
        randomly between (0,5)
        '''
        import random
        #A sigma value is the standard deviation of the distribution
        #Choose a arbitrary sigma value by using random.uniform method and by
        #using this value we will create a kernel with size 6*sigma x 6*sigma
        sigma = random.uniform(0,5)
        n = int(6*sigma)
        if n % 2 == 0:
            n += 1
        g = 1/(2*math.pi*(sigma**2))
        kernel = []
        #To compute values of kernel we will use 2D, isotropoic Gaussian
        #distribution function
        for y in range(n):
            kernel.append([])
            for x in range(n):
                p = math.exp(-( (abs(n//2 - x)**2 + abs(n//2 - y)**2) / (2 * (sigma**2))))
                kernel[y].append(g*p)
        result = self.correlation(kernel)
        result.clip()
        return result
    
    def rotating(self):
        result = Image.new(self.height, self.width)
        for x in reversed(range(self.width)):
            for y in range(self.height):
                result.set_pixel(y, x, self.pixels[y*self.width + x])
        return result
    
    def lowest_column(self):
        values = [0] * self.width
        result = self.edges()
        for x in range(result.width):
            for y in range(result.height):
                values[x] += result.pixels[y * result.width + x]
        return values.index(min(values))
    
    def remove_column(self, x):
        """
        Mutates self by removing pixels in the column x.
        """
        #remove pixels from the end, so that it doesn't affect location of others
        for y in reversed(range(self.height)):
            self.pixels.pop(y*self.width + x)
        self.width -= 1
    
    def content_aware_scaling(self, n):
        result = Image.new(self.width, self.height)
        result.pixels = self.pixels[:] 
        for k in range(n):
            i = result.lowest_column()
            result.remove_column(i)
        return result
        
        
    
    # Below this point are utilities for loading, saving, and displaying
    # images, as well as for testing.

    def __eq__(self, other):
        return all(getattr(self, i) == getattr(other, i)
                   for i in ('height', 'width', 'pixels'))

    def __repr__(self):
        return "Image(%s, %s, %s)" % (self.width, self.height, self.pixels)

    @classmethod
    def load(cls, fname):
        """
        Loads an image from the given file and returns an instance of this
        class representing that image.  This also performs conversion to
        grayscale.

        Invoked as, for example:
           i = Image.load('test_images/cat.png')
        """
        with open(fname, 'rb') as img_handle:
            img = PILImage.open(img_handle)
            img_data = img.getdata()
            if img.mode.startswith('RGB'):
                pixels = [round(.299*p[0] + .587*p[1] + .114*p[2]) for p in img_data]
            elif img.mode == 'LA':
                pixels = [p[0] for p in img_data]
            elif img.mode == 'L':
                pixels = list(img_data)
            else:
                raise ValueError('Unsupported image mode: %r' % img.mode)
            w, h = img.size
            return cls(w, h, pixels)

    @classmethod
    def new(cls, width, height):
        """
        Creates a new blank image (all 0's) of the given height and width.

        Invoked as, for example:
            i = Image.new(640, 480)
        """
        return cls(width, height, [0 for i in range(width*height)])

    def save(self, fname, mode='PNG'):
        """
        Saves the given image to disk or to a file-like object.  If fname is
        given as a string, the file type will be inferred from the given name.
        If fname is given as a file-like object, the file type will be
        determined by the 'mode' parameter.
        """
        out = PILImage.new(mode='L', size=(self.width, self.height))
        out.putdata(self.pixels)
        if isinstance(fname, str):
            out.save(fname)
        else:
            out.save(fname, mode)
        out.close()

    def gif_data(self):
        """
        Returns a base 64 encoded string containing the given image as a GIF
        image.

        Utility function to make show_image a little cleaner.
        """
        buff = BytesIO()
        self.save(buff, mode='GIF')
        return base64.b64encode(buff.getvalue())

    def show(self):
        """
        Shows the given image in a new Tk window.
        """
        global WINDOWS_OPENED
        if tk_root is None:
            # if tk hasn't been properly initialized, don't try to do anything.
            return
        WINDOWS_OPENED = True
        toplevel = tkinter.Toplevel()
        # highlightthickness=0 is a hack to prevent the window's own resizing
        # from triggering another resize event (infinite resize loop).  see
        # https://stackoverflow.com/questions/22838255/tkinter-canvas-resizing-automatically
        canvas = tkinter.Canvas(toplevel, height=self.height,
                                width=self.width, highlightthickness=0)
        canvas.pack()
        canvas.img = tkinter.PhotoImage(data=self.gif_data())
        canvas.create_image(0, 0, image=canvas.img, anchor=tkinter.NW)
        def on_resize(event):
            # handle resizing the image when the window is resized
            # the procedure is:
            #  * convert to a PIL image
            #  * resize that image
            #  * grab the base64-encoded GIF data from the resized image
            #  * put that in a tkinter label
            #  * show that image on the canvas
            new_img = PILImage.new(mode='L', size=(self.width, self.height))
            new_img.putdata(self.pixels)
            new_img = new_img.resize((event.width, event.height), PILImage.NEAREST)
            buff = BytesIO()
            new_img.save(buff, 'GIF')
            canvas.img = tkinter.PhotoImage(data=base64.b64encode(buff.getvalue()))
            canvas.configure(height=event.height, width=event.width)
            canvas.create_image(0, 0, image=canvas.img, anchor=tkinter.NW)
        # finally, bind that function so that it is called when the window is
        # resized.
        canvas.bind('<Configure>', on_resize)
        toplevel.bind('<Configure>', lambda e: canvas.configure(height=e.height, width=e.width))

        # when the window is closed, the program should stop
        toplevel.protocol('WM_DELETE_WINDOW', tk_root.destroy)


try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
    tcl = tkinter.Tcl()
    def reafter():
        tcl.after(500,reafter)
    tcl.after(500,reafter)
except:
    tk_root = None
WINDOWS_OPENED = False

if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    pass

    # the following code will cause windows from Image.show to be displayed
    # properly, whether we're running interactively or not:
    if WINDOWS_OPENED and not sys.flags.interactive:
        tk_root.mainloop()
