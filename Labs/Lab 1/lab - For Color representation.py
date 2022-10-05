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
        self.height = height
        # A list of pixel values (0 - 255) stored in row-major order
        self.pixels = pixels
        
    def get_pixel(self, x, y):
        '''Returns the pixel value of the image at the position of (x,y)'''
        return self.pixels[self.width * y + x]
    
    def get_pixel_extended(self, x, y):
        '''
        Helper function for apply_kernel
        Returns the pixel of the image at the position (x, y).
        If given position (x, y) is out of range, returns the nearest valid pixel
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
        '''Set the pixel value of the image at the position of (x,y)
        to the given value c'''
        self.pixels[self.width * y + x] = c

    def apply_per_pixel(self, func):
        '''
        Apply given function 'func' to the every pixel value of image
        '''
        result = Image.new(self.width, self.height)
        for y in range(result.height):
            for x in range(result.width):
                color = self.get_pixel(x, y)
                newcolor = func(color)
                result.set_pixel(x, y, newcolor)
        return result

    def clip(self):
        '''
        Helper function for apply_kernel and filters
        Clip the negative pixel values to 0 and values > 255 to 255, and convert
        every pixel value to an integer to ensure that there is no float number
        '''
        for i in range(len(self.pixels)):
            self.pixels[i] = round(self.pixels[i])
            if self.pixels[i] > 255:
                self.pixels[i] = 255
            if self.pixels[i] < 0:
                self.pixels[i] = 0
                
    def apply_kernel(self, x, y, size, kernel):
        '''
        Apply the given kernel to the pixel value of the image at the position of (x,y)
        '''
        new_pixel_value = 0
        y1 = -1
        for j in range(y-size,y+size+1):
            y1 += 1 
            x1 = -1
            for i in range(x-size,x+size+1):
                x1 += 1
                new_pixel_value += self.get_pixel_extended(i, j) * kernel[y1][x1]
        return new_pixel_value
    
    def inverted(self):
        '''Reflects the pixels about the middle gray value
        Ex: 0 becomes 255 after inversion'''
        return self.apply_per_pixel(lambda c: 255-c)
    
    def correlation(self, kernel):
        '''
        Apply the given kernel to the every pixel value of the given image
        '''
        result = Image.new(self.width, self.height)
        size = len(kernel)//2
        for y in range(self.height):
            for x in range(self.width):
                c = self.apply_kernel(x, y, size, kernel)
                result.set_pixel(x, y, c)
        return result
                
    def blurred(self, n):
        '''
        Creates a kernel with size nxn and apply to the given image
        '''
        kernel = [[1/(n**2) for i in range(n)] for i in range(n)]
        result = self.correlation(kernel)
        result.clip()
        return result

    def sharpened(self, n):
        '''
        Apply the unsharp mask to the given image
        '''
        kernel = [[-1/(n**2) for i in range(n)] for i in range(n)]
        kernel[n//2][n//2] += 2
        result = self.correlation(kernel)
        result.clip()
        return result

    def edges(self):
        '''
        Detects the edges of the given image
        '''
        kernel_x = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        kernel_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
        size = len(kernel_x)//2
        result = Image.new(self.width, self.height)
        
        for y in range(self.height):
            for x in range(self.width):
                o_x = self.apply_kernel(x, y, size, kernel_x)
                o_y = self.apply_kernel(x, y, size, kernel_y)
                o_xy = round(math.sqrt(o_x**2 + o_y**2))
                result.set_pixel(x, y, o_xy)
                
        result.clip()
        return result
    
    def min_energy_column(self):
        '''
        Returns the position of the column that has minimum energy value
        '''
        min_energy = self.height * 255
        column_energy = 0
        column_position = 0
        for x in range(self.width):
            column_energy = 0
            for y in range(self.height):
                column_energy += self.get_pixel(x, y)
            if column_energy < min_energy:
                min_energy = column_energy
                column_position = x
        return column_position
        
    def remove_column(self, min_col):
        '''
        Removes the column at the position of min_col
        '''
        for y in range(self.height-1,-1,-1):
            self.pixels.pop(y * self.width + min_col)
        self.width -= 1
    
    def retargeting(self, crop_size):
        '''
        Decrease the width of the given image by length of crop_size
        while trying to preserve the main subjects of the image
        '''
        result = Image(self.width, self.height, self.pixels)    
        for c in range(crop_size):
            energy_map = result.edges()
            lowest_energy_column = energy_map.min_energy_column()
            result.remove_column(lowest_energy_column)
            
        return result

    def cumulative_energy_map(self):
        '''
        Creates and returns a cumulative energy map that is each pixels value is the minimum
        cost to reach from top row to that pixel
        '''
        cum_map = Image(self.width, self.height, self.pixels)
        for y in range(1, self.height):
            for x in range(self.width):
                if x == 0:
                    min_val = min(cum_map.get_pixel(x,y-1), cum_map.get_pixel(x+1,y-1))
                if x == self.width - 1:
                    min_val = min(cum_map.get_pixel(x-1,y-1), cum_map.get_pixel(x,y-1))
                elif x > 0 and x < (self.width - 1):
                    min_val = min(cum_map.get_pixel(x-1,y-1), cum_map.get_pixel(x,y-1), cum_map.get_pixel(x+1,y-1))
                cum_map.pixels[y*self.width + x] += min_val
        return cum_map
    
    def min_cost_path(self):
        '''
        Find the minimum cost path to reach from top row to the bottom row
        on the cumulative energy map
        '''
        path = []
        w = self.width
        h = self.height
        min_index = self.pixels[w*(h - 1):w*h].index(min(self.pixels[w*(h - 1):w*h]))
        path.append(min_index)
        for y in range(self.height - 1, 0, -1):
            x = path[-1]
            if x == 0:
                d = {self.get_pixel(x,y-1): x, self.get_pixel(x+1,y-1): x+1}
            if x == (self.width - 1):
                d = {self.get_pixel(x-1,y-1): x-1, self.get_pixel(x,y-1): x}
            elif x > 0 and x < (self.width - 1):
                d = {self.get_pixel(x-1,y-1): x-1, self.get_pixel(x,y-1): x, self.get_pixel(x+1,y-1): x+1}
            min_index = d[min(d)]
            path.append(min_index)
        
        return path
            
    def remove_path(self, min_cost_path):
        '''
        Removes the pixels which their position are given with min_cost_path list
        '''
        for y in range(self.height-1,-1,-1):
            index = min_cost_path[(self.height-1)-y]
            self.pixels.pop(y*self.width + index)
        self.width -= 1
            
    def seam_carving(self, crop_size):
        '''
        Decrease the width of the given image by length of crop_size
        while trying to preserve the main subjects of the image
        (with seam carving technique)
        '''
        result = Image(self.width, self.height, self.pixels)
        for c in range(crop_size):
            energy_map = result.edges()
            cumulative_map = energy_map.cumulative_energy_map()
            lowest_cost_path = cumulative_map.min_cost_path()
            result.remove_path(lowest_cost_path)
            
        return result
    
    def separate_color_image(self):
        '''
        Returns 3 greyscale pictures which are equivalents of the R G B
        components of the given color image
        '''
        red = Image.new(self.width, self.height)
        green = Image.new(self.width, self.height)
        blue = Image.new(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                pixel = self.get_pixel(x, y)
                red.set_pixel(x, y, pixel[0])
                green.set_pixel(x, y, pixel[1])
                blue.set_pixel(x, y, pixel[2])
                
        return red, green, blue
    
    def merge_images(self, red, green, blue):
        '''
        Merge the 3 greyscale image to create an 1 color image and returns
        the result
        '''
        for y in range(self.height):
            for x in range(self.width):
                pixel = (red.get_pixel(x,y), green.get_pixel(x,y), blue.get_pixel(x,y))
                self.set_pixel(x, y, pixel)
    
    def apply_color_filter(self):
        '''
        Apply the given filter 'filt' to the color image
        '''
        result = Image.new(self.width, self.height)
        r, g, b = self.separate_color_image()
        result.merge_images(r.blurred(7), g.blurred(7), b.blurred(7))
        return result
    
    def seam_carving_color(self, crop_size):
        '''
        Decrease the width of the given color image by length of 
        crop_size while trying to preserve the main subjects of 
        the image (with seam carving technique)
        '''
        result = Image(self.width, self.height, self.pixels)
        for c in range(crop_size):
            grayscale_copy = result.grayscale_image_from_color_image()
            energy_map = grayscale_copy.edges()
            cumulative_map = energy_map.cumulative_energy_map()
            lowest_cost_path = cumulative_map.min_cost_path()
            result.remove_path(lowest_cost_path)
            
        return result
    
    def grayscale_image_from_color_image(self):
        '''
        Creates and returns a grayscale copy of the color image based on 
        luminosities which is represented by the formula:
            0.299 * R + 0.587 * G + 0.114 * B
        '''
        result = Image.new(self.width, self.height)
        r, g, b = self.separate_color_image()
        for y in range(self.height):
            for x in range(self.width):
                pixel = round(0.299*r.get_pixel(x, y) + 0.587 * g.get_pixel(x, y) + 0.114 * b.get_pixel(x, y))
                result.set_pixel(x, y, pixel)
                
        return result
    
    def threshold_filter_color(self, threshold_value):
        '''
        Replaces the pixel values of the color image which are above the threshold_value 
        with 255 and below the threshold_value with 0
        '''
        result = Image.new(self.width, self.height)
        r, g, b = self.separate_color_image()
        
        for im in (r, g, b):
            im.threshold_filter_grayscale(threshold_value)
            
        result.merge_images(r, g, b)
        
        return result
                
    def threshold_filter_grayscale(self, threshold_value):
        '''
        Replaces the pixel values of the given image which are above the 
        threshold_value with 255 and below the threshold_value with 0
        '''
        for y in range(self.height):
            for x in range(self.width):
                pixel_value = self.get_pixel(x, y)
                if pixel_value > threshold_value:
                    self.set_pixel(x, y, 255)
                else:
                    self.set_pixel(x, y, 0)
                    
    def embossing(self, kernel):
        '''
        Enhances the edges of the image in the direction of the given kernel
        '''
        result = Image.new(self.width, self.height)
        grayscale_copy = self.grayscale_image_from_color_image()
        result = grayscale_copy.correlation(kernel)
        
        return result
    
    def pasting_image(self, img):
        '''
        Paste smaller image on top of the bigger image
        '''
        assert(self.width >= img.width and self.height >= img.height)
        
        result = Image(self.width, self.height, self.pixels)
        
        for y in range(img.height):
            for x in range(img.width):
                pixel = img.get_pixel(x, y)
                result.set_pixel(x, y, pixel)
        
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
    def load_color_image(cls, fname):
        """
        Loads a color image from the given file and returns a dictionary
        representing that image.
        
        Invoked as, for example:
           i = load_image('test_images/cat.png')
        """
        with open(fname, 'rb') as img_handle:
            img = PILImage.open(img_handle)
            img = img.convert('RGB')  # in case we were given a greyscale image
            img_data = img.getdata()
            pixels = list(img_data)
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
        
    def save_color_image(self, fname, mode = 'PNG'):
        """
        Saves the given color image to disk or to a file-like object.  If filename
        is given as a string, the file type will be inferred from the given name.
        If filename is given as a file-like object, the file type will be
        determined by the 'mode' parameter.
        """
        out = PILImage.new(mode='RGB', size=(self.width, self.height))
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
    
#    #Testing for correlation method
#    im1 = Image.load('test_images/pigbird.png')
#    kernel = [[0 for i in range(9)] for i in range(9)]
#    kernel[2][0] = 1
#    result1 = im1.correlation(kernel)
#    result1.save('test_results/pigbird_test_kernel_9x9.png')
#    
#    #Testing for the blur filter
#    im2 = Image.load('test_images/cat.png')
#    result2 = im2.blurred(5)
#    result2.save('test_results/cat_test_blur_kernel_5x5.png')
#    
#    #Testing for the sharpened filter
#    im3 = Image.load('test_images/python.png')
#    result3 = im3.sharpened(11)
#    result3.save('test_results/python_test_sharpened_kernel_11x11.png')
#    
#    #Discovering the kernels of the edge filter
#    im4 = Image.load('test_images/construct.png')
#    kernel_x = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
#    kernel_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
#    result_x = im4.correlation(kernel_x)
#    result_x.save('test_results/construct_kernel_x.png')
#    result_y = im4.correlation(kernel_y)
#    result_y.save('test_results/construct_kernel_y.png')
#    
#    #Testing the edge detection filter
#    result4 = im4.edges()
#    result4.save('test_results/construct_edge_filter.png')
#    result5 = im2.edges()
#    result5.save('test_results/cat_edge_filter.png')
#    
#    #Server tests
#    for image_name in ('centered_pixel', 'pattern', 'blob'):
#        im = Image.load('test_images/' + image_name + '.png')
#        result = im.inverted()
#        result.save('test_results/' + image_name + '_inversion_test' + '.png')
#        result = im.blurred(3)
#        result.save('test_results/' + image_name + '_blur_filter_3x3_kernel_test' + '.png')
#        result = im.sharpened(3)
#        result.save('test_results/' + image_name + '_sharpened_filter_3x3_kernel_test' + '.png')
#        if image_name != 'blob':
#            result = im.edges()
#            result.save('test_results/' + image_name + '_edge_filter_test' + '.png')
    
#    #Test for the retargeting 
#    for image_name in ('tree', 'twocats', 'pigbird'):
#        im = Image.load('test_images/' + image_name + '.png')
#        if image_name == 'tree':
#            crop_size = 75
#        else:
#            crop_size = 100
#        result = im.retargeting(crop_size)
#        result.save('test_results/' + image_name + '_retargeting_test' + '.png')
    
    #Cumulative Energy Map Test
#    im = Image(3, 3, [1, 2, 3, 1, 2, 3, 1, 2, 3])
#    edge = im.edges()
#    print(edge.cumulative_energy_map())
#    
#    im2 = Image(4, 4, [i%4 for i in range(16)])
#    edge2 = im2.edges()
#    print(edge2)
#    print(edge2.cumulative_energy_map())
    
    #Path finding test
#    im = Image(4, 4, [1, 2, 3, 4, 6, 3, 4, 5, 4, 6, 1, 2, 5, 7, 2, 3])
#    print(im.min_cost_path())
    
    #Testing for the seam carving
#    im = Image.load('test_images/twocats.png')
#    result = im.seam_carving(100)
#    result.save('test_results/twocats_seam_carving.png')
    
#    im2 = Image.load('test_images/pigbird.png')
#    result2 = im2.seam_carving(100)
#    result2.save('test_results/pigbird_seam_carving.png')
    
    #Color image separation test
#    im = Image.load_color_image('test_images/twocats.png')
#    result = im.seam_carving_color(100)
#    result.save_color_image('test_results/twocats_color_seam_carving.png')
    
    #Threshold filter testing
#    im = Image.load_color_image('test_images/mushroom.png')
#    for i in range(0,256,10):
#        result = im.threshold_filter_color(i)
#        result.save_color_image('test_results/threshold_filter/mushroom_' + str(i) + '_threshold_value.png')
    
    #Testing the emboss filter
#    im = Image.load_color_image('test_images/construct.png')
#    kernel_1 = [[0, 1, 0], [0, 0, 0], [0, -1, 0]]
#    kernel_2 = [[0, 0, 0], [1, 0, -1], [0, 0, 0]]
#    kernel_3 = [[1, 0, 0], [0, 0, 0], [0, 0, -1]]
#    result = im.embossing(kernel_1)
#    result.save('test_results/construct_ver_emboss.png')
#    result = im.embossing(kernel_2)
#    result.save('test_results/construct_hor_emboss.png')
#    result = im.embossing(kernel_3)
#    result.save('test_results/construct_diagonal_emboss.png')    
    
#    #Testing image paste
#    im1 = Image.load_color_image('test_images/construct.png')
#    im2 = Image.load_color_image('test_images/cat.png')
#    result = im1.pasting_image(im2)
#    result.save_color_image('test_results/construct_paste_cat.png')
        
    # the following code will cause windows from Image.show to be displayed
    # properly, whether we're running interactively or not:
    if WINDOWS_OPENED and not sys.flags.interactive:
        tk_root.mainloop()
