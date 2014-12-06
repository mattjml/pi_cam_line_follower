import sys
import cv2
from cv2 import cv
import numpy as np
#from matplotlib import pyplot
import operator
from datetime import datetime

from util import Time_It

PRINT_TIME_DELTAS = False

class Line_Analyser(object):
    def _waitKey():
        key = cv2.waitKey()
        if chr(key).lower() == 'q':
            sys.exit(1)

    def find_local_extrema(self, hist, op = operator.lt):
        hist_len = len(hist)    
        last_index = hist_len - 1
        unfiltered_extrema = [index for index in xrange(hist_len) if (index == 0 and op(hist[0],hist[1])) or (index == last_index and op(hist[last_index],hist[last_index - 1])) or (index > 0 and index < last_index and op(hist[index],hist[index-1]) and op(hist[index],hist[index+1]))]
        return [unfiltered_extrema[index] for index in xrange(len(unfiltered_extrema)) if index == 0 or unfiltered_extrema[index-1] + 1 != unfiltered_extrema[index]]

    def make_binary_image(self, img, demo_hist_plot=False, demo_threshold=False, demo_erode=False):
        ''' '''
        
        def find_extrema(histogram):
            ''' '''
            initial_maxima = self.find_local_extrema(histogram, operator.ge)
            extrema_threshold = 0
            maxima = []
            while len(maxima) < 2:
                extrema_threshold += .05
                if extrema_threshold >= 1.0:
                    return 1
                tmp_maxima = [index for index in initial_maxima if histogram[index] > extrema_threshold]
                maxima = [tmp_maxima[x] for x in range(len(tmp_maxima)) if x == 0 or (tmp_maxima[x-1] + 20) < tmp_maxima[x]]
           
            minima = [index for index in self.find_local_extrema(histogram, operator.le) if histogram[index] < extrema_threshold]
            possible_minima = [index for index in minima if index > maxima[0] and index < maxima[1]]
            return min(possible_minima)
       
        def img_threshold(img, threshold_method, threshold, demo=False):
            ''' '''
    
            ret,img_thresh = cv2.threshold(img,threshold,255,cv2.THRESH_BINARY)        
            return img_thresh
    
        def erode_and_dilate(image, demo=False):
            ''' '''
            kernel = np.ones((3,3),np.uint8)
            img_erode = cv2.erode(image,kernel,iterations = 2)
            img_dilate = cv2.dilate(img_erode,kernel,iterations = 3)
            #if demo:
                #cv2.imshow('erode',img_erode)
                #waitKey()
                #cv2.imshow('dilate',img_dilate)
                #waitKey()
            return img_dilate     

        hist,bins = np.histogram(img.ravel(),256,[0,256])
        hist = hist.astype(float)/max(hist)
        #print hist
        threshold = find_extrema(hist)
        #print("Chosen threshold {0}".format(threshold))
         
        #if demo_hist_plot:
            #pyplot.hist(img.ravel(),256,[0,256]);
            #pyplot.show()
    
        img = img_threshold(img, cv2.THRESH_BINARY, threshold, demo_threshold)
        img = erode_and_dilate(img, demo_erode) 
        img = img_threshold(img, cv2.THRESH_BINARY, 10, demo_threshold)

        return img

    def intersect_lines(self, img, interval_percent, demo=False):
        '''Takes an input opencv binary image and returns the horizontal line
        intersections at different vertical postitions throughout the image.
        Returns dictionary with vertical positions (as percentages) as keys
        and a list of tuples giving the start and end horizontal positions of
        line intersections.'''
        
        dsp_img = img.copy()
        imheight = img.shape[0]
        imwidth = img.shape[1]
        lines = {}
        for y_pc in range(0,51,interval_percent) + range(-interval_percent, -50, -interval_percent):
            y = int((y_pc * imheight * 0.01) + (imheight/2 - 1))
            max_index = imwidth - 1
       
            intersections = [index for index in xrange(imwidth) if index == 0 or index == max_index or (not img[y][index]) != (not img[y][index-1])]
    
            if img[y][intersections[0]] > 0:
                intersections = intersections[1:]
            if len(intersections) % 2 == 1:
                intersections = intersections[:-1]
            
            lines[y_pc] = [((intersections[i]*100)/imwidth, (intersections[i+1]*100)/imwidth) for i in xrange(0,len(intersections),2)]
            if True:
                for line in lines[y_pc]:
                    for i in range((line[0]*imwidth)/100, (line[1]*imwidth)/100):
                        dsp_img[y][i] = 125
    
        if demo:
            cv2.imshow('scan_lines', dsp_img)
            waitKey()
        cv2.imwrite('/root/img_{}.jpeg'.format(datetime.now()),dsp_img)
        print("writing to img")
        return lines

    def get_lines(self, img, interval_percent=10, demo_thresholds=False, demo_lines=False):
        lines = None
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
        overall_timeit = Time_It('Overall')
    
        binary_timeit = Time_It('Binary')
        img = self.make_binary_image(img, demo_hist_plot=False, demo_threshold=False, demo_erode=False)
        binary_timeit.finish()
        #print(binary_timeit)
    
        find_lines_timeit = Time_It('Find Lines')
        lines = self.intersect_lines(img, interval_percent, demo=demo_lines)
        find_lines_timeit.finish()
        #print(find_lines_timeit)
    
        overall_timeit.finish()
        #print(overall_timeit)

        return lines

def test_line_analysis(path):
    analyser = Line_Analyser()
    img = cv2.imread(path)
    assert analyser.get_lines(img, 10, demo_thresholds=False, demo_lines=False) is not None

if __name__ == '__main__':
    test_line_analysis(sys.argv[1])

