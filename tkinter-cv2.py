import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import numpy as np

class Camera():
    def __init__(self,imgwidth =720, imgheight=576, webcam = True):
        self.width = imgwidth
        self.height =  imgheight
        self.finalwidth = 720
        self.finalheight = 576
        self.pts1 = [[0,0],[200,0],[100,500],[250,500]]
        self.min_area = 50
        if webcam == True:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3,self.width)
            self.cap.set(4,self.height)



    def originalimage(self):
        success, img = self.cap.read()
        if success:
            return img

    def Warp_perspective(self):  # pts1 to be in a list format [[],[],[],[]]
        success, img = self.cap.read()
        if success:
            pts1 = np.float32(self.pts1)
            pts2 = np.float32(
                [[0, 0], [self.finalwidth, 0], [0, self.finalheight], [self.finalwidth, self.finalheight]])
            self.matrix = cv2.getPerspectiveTransform(pts1, pts2)
            warpimg = cv2.warpPerspective(img, self.matrix, (self.finalwidth, self.finalheight))

            return warpimg

    def setWarp_Bounding_Box(self,coordinates):
        self.__setattr__(self.pts1, coordinates)

class App(tk.Tk,Camera):
    def __init__(self,*args,**kwargs):
        tk.Tk.__init__(self,*args,**kwargs)
        Camera.__init__(self)                           #instantiating Camera class


        container = tk.Frame(self)                      #container is the main instance of Frame for our controller

        container.pack(side = "top",fill = "both", expand = True)
        container.grid_rowconfigure(0,weight = 1)
        container.grid_columnconfigure(0,weight = 1)

        self.frames = {}                                  #creating a dictionary for all the different frames

        for F in (OriginalView,WarpPerspective):
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0,sticky = "nsew")

        self.show_frame(OriginalView)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()




class OriginalView(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text = "Original Image")
        label.pack(pady=10, padx=10)
        self.cont = cont
        self.delay = 50

        self.canvas = tk.Canvas(self, width = cont.width, height = cont.height)
        self.canvas.pack()
        button = tk.Button(self,text = "press me",command = lambda: cont.show_frame(WarpPerspective))
        button.pack()
        self.update_canvas()

    def update_canvas(self):
        self.img = self.cont.originalimage()
        self.img = cv2.cvtColor(self.img,cv2.COLOR_BGR2RGB)
        self.img = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.img))
        self.canvas.create_image(0,0,image = self.img, anchor = 'nw')
        self.after(self.delay,self.update_canvas)



class WarpPerspective(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Original Image")
        label.pack(pady=10, padx=10)
        self.cont = cont
        self.delay = 50

        self.canvas = tk.Canvas(self, width=cont.width, height=cont.height)
        self.canvas.pack()
        button = tk.Button(self, text="press me", command=lambda: cont.show_frame(OriginalView))
        button.pack()
        self.update_canvas()

    def update_canvas(self):
        self.img = self.cont.Warp_perspective()
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        self.img = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.img))
        self.canvas.create_image(0, 0, image=self.img, anchor='nw')
        self.after(self.delay, self.update_canvas)


app = App()
app.mainloop()
