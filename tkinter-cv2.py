import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import numpy as np

class Camera():
    def __init__(self):
        pt1 = [[0, 0], [0, 0], [0, 0], [0, 0]]
        self.pts1 = pt1
        self.min_area = 50
        self.cap = cv2.VideoCapture(0)
        self.finalwidth = 640
        self.finalheight = 480
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.DataArray = None
        self.Threshold = [[],[]]

    def getContour(self, img, imgshow):
        contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        coordinate = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # print(area)
            if area > 500:
                cv2.drawContours(img, cnt, -1, (255, 0, 0), 3)
                peri = cv2.arcLength(cnt, True)
                # print(peri)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
                # print(len(approx))
                # objCor = len(approx)
                x, y, w, h = cv2.boundingRect(approx)
                coordinate.append([x, y, w, h])
                cv2.rectangle(imgshow, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return imgshow

    def stackImages(self, scale, imgArray):
        rows = len(imgArray)
        cols = len(imgArray[0])
        rowsAvailable = isinstance(imgArray[0], list)
        width = imgArray[0][0].shape[1]
        height = imgArray[0][0].shape[0]
        if rowsAvailable:
            for x in range(0, rows):
                for y in range(0, cols):
                    if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
                        imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                    else:
                        imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]),
                                                    None, scale, scale)
                    if len(imgArray[x][y].shape) == 2: imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
            imageBlank = np.zeros((height, width, 3), np.uint8)
            hor = [imageBlank] * rows
            hor_con = [imageBlank] * rows
            for x in range(0, rows):
                hor[x] = np.hstack(imgArray[x])
            ver = np.vstack(hor)
        else:
            for x in range(0, rows):
                if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                    imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
                else:
                    imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None, scale,
                                             scale)
                if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
            hor = np.hstack(imgArray)
            ver = hor
        return ver

    def Canny(self,img):
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (7, 7), 1)  # higher the value of sigma, the more blur it gets
        imgCanny = cv2.Canny(imgBlur, 50, 50)
        return imgCanny

    def originalimage(self):
        success, img = self.cap.read()
        if success:
            return img

    def Warp_perspective(self,pts1,img):  # pts1 to be in a list format [[],[],[],[]]

        self.pts1 = pts1
        pts1 = np.float32(self.pts1)
        pts2 = np.float32([[0, 0], [self.finalwidth, 0], [0, self.finalheight], [self.finalwidth, self.finalheight]])
        self.matrix = cv2.getPerspectiveTransform(pts1, pts2)
        warpimg = cv2.warpPerspective(img, self.matrix, (self.finalwidth, self.finalheight))

        return warpimg

    def HSV_Calibration(self,Array):
        success, img  = self.cap.read()
        HSVimg = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        lower = np.array(Array[0])
        upper = np.array(Array[1])
        mask = cv2.inRange(HSVimg,lower,upper)
        imgresult = cv2.bitwise_and(img,img,mask = mask)
        return mask, imgresult

class App(tk.Tk,Camera):
    def __init__(self,*args,**kwargs):
        tk.Tk.__init__(self,*args,**kwargs)
        Camera.__init__(self)         #instantiating Camera class

        self.delay = 110
        container = tk.Frame(self)                      #container is the main instance of Frame for our controller
        container.pack(side = 'top', fill = 'both', expand = True)

        container.grid_rowconfigure(0,weight = 1)
        container.grid_columnconfigure(0,weight = 1)

        self.frames = {}                                  #creating a dictionary for all the different frames

        for F in (OriginalView,WarpPerspective,HueSaturation,ContourDetection):
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky ='nsew')
            # frame.grid_columnconfigure(0,weight = 1)
            # frame.grid_rowconfigure(0,weight =  1)



        ##Show Menu bar###
        self.mymenu = tk.Menu(self)
        self.config(menu=self.mymenu)
        CameraCalibration = tk.Menu(self.mymenu)
        LinearStage = tk.Menu(self.mymenu)

        self.mymenu.add_cascade(label="Camera", menu=CameraCalibration)
        self.mymenu.add_cascade(label="LinearStage", menu=LinearStage)
        CameraCalibration.add_command(label="Original Image", command= lambda:self.show_frame(OriginalView))
        CameraCalibration.add_command(label = "WarpPerspective",command = lambda: self.show_frame(WarpPerspective))
        CameraCalibration.add_command(label = "HSVCalibration", command = lambda:self.show_frame(HueSaturation))
        CameraCalibration.add_command(label = "ContourDetection", command = lambda:self.show_frame(ContourDetection))

        self.show_frame(OriginalView)


    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()




class OriginalView(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self,parent)
        self.label = tk.Label(self, text = "Original Image")
        self.label.grid(row = 0, column = 1,sticky = "nsew")
        self.cont = cont
        self.canvas = tk.Canvas(self,height =cont.height, width = cont.width ,bg = "red",bd =None)
        self.canvas.grid(row = 1, column = 1)
        self.button = tk.Button(self,text = "WarpPerspectiveMode",command = lambda: cont.show_frame(WarpPerspective))
        self.button.grid(row = 2,column = 1)
        self.button1 = tk.Button(self, text="HueSaturation", command=lambda: cont.show_frame(HueSaturation))
        self.button1.grid(row=2, column=2)
        self.update_canvas()

    def update_canvas(self):
        self.img = self.cont.originalimage()
        self.img = cv2.cvtColor(self.img,cv2.COLOR_BGR2RGB)
        self.img = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.img))
        self.canvas.create_image(2,2,image = self.img,anchor = tk.NW)
        self.after(self.cont.delay,self.update_canvas)




class WarpPerspective(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text="Warp Image")
        self.label.grid(row = 1, column = 2)
        self.cont = cont
        self.calibrateimagedone = True
        self.calibrateconfirm = False
        self.x_val = 0
        self.y_val = 0


        self.canvas = tk.Canvas(self, height=cont.height, width=cont.width)
        self.canvas.grid(row=2, column=1, columnspan=4)

        self.calibrationbutton = tk.Button(self,text = "Calibration Image",command = lambda:self.Warp_Calibration_image())
        self.calibrationbutton.grid(row = 3, column = 4)

        self.confirmbutton = tk.Button(self, text = "Confirm Calibration", command = lambda:self.Confirm_Calibration())
        self.confirmbutton.grid(row=4, column = 4)



        self.HSVpage = tk.Button(self,text = "HSV PAGE",command = lambda: self.cont.show_frame(HueSaturation))
        self.HSVpage.grid(row = 5,column = 4)

        #-------tkinter values -----------
        self.x1coordinate = tk.IntVar()
        self.y1coordinate = tk.IntVar()
        self.x2coordinate = tk.IntVar()
        self.y2coordinate = tk.IntVar()
        self.x3coordinate = tk.IntVar()
        self.y3coordinate = tk.IntVar()
        self.x4coordinate = tk.IntVar()
        self.y4coordinate = tk.IntVar()



        #------- Coordinates Entry Box--------------
        self.entryboxframe = tk.LabelFrame(self, text="Coordinates", pady=10, padx=10)
        self.entryboxframe.grid(row=4, column=1)

        self.label1x = tk.Label(self.entryboxframe,text = "X1:")
        self.label1x.grid(row = 3, column =1,sticky = "SE")
        self.label1y = tk.Label(self.entryboxframe,text = "Y1:")
        self.label1y.grid(row = 3, column =3, sticky = "NW")
        self.x1value = tk.Entry(self.entryboxframe,width = 5,textvariable = self.x1coordinate)
        self.x1value.grid(row = 3,column = 2, sticky = "NW")
        self.y1value = tk.Entry(self.entryboxframe,width = 5,textvariable = self.y1coordinate)
        self.y1value.grid(row=3, column=4, sticky="NW")

        self.label2x = tk.Label(self.entryboxframe, text="X2:")
        self.label2x.grid(row=4, column=1, sticky="SE")
        self.label2y = tk.Label(self.entryboxframe, text="Y2:")
        self.label2y.grid(row=4, column=3, sticky="NW")
        self.x2value = tk.Entry(self.entryboxframe, width=5, textvariable=self.x2coordinate)
        self.x2value.grid(row=4, column=2, sticky="NW")
        self.y2value = tk.Entry(self.entryboxframe, width=5, textvariable=self.y2coordinate)
        self.y2value.grid(row=4, column=4, sticky="NW")

        self.label3x = tk.Label(self.entryboxframe, text="X3:")
        self.label3x.grid(row=5, column=1, sticky="SE")
        self.label3y = tk.Label(self.entryboxframe, text="Y3")
        self.label3y.grid(row=5, column=3, sticky="NW")
        self.x3value = tk.Entry(self.entryboxframe, width=5, textvariable=self.x3coordinate)
        self.x3value.grid(row=5, column=2, sticky="NW")
        self.y3value = tk.Entry(self.entryboxframe, width=5, textvariable=self.y3coordinate)
        self.y3value.grid(row=5, column=4, sticky="NW")

        self.label4x = tk.Label(self.entryboxframe, text="X4:")
        self.label4x.grid(row=6, column=1, sticky="SE")
        self.label4y = tk.Label(self.entryboxframe, text="Y4")
        self.label4y.grid(row=6, column=3, sticky="NW")
        self.x4value = tk.Entry(self.entryboxframe, width=5, textvariable=self.x4coordinate)
        self.x4value.grid(row=6, column=2, sticky="NW")
        self.y4value = tk.Entry(self.entryboxframe, width=5, textvariable=self.y4coordinate)
        self.y4value.grid(row=6, column=4, sticky="NW")

        self.update_canvas()

    def update_canvas(self):
        if self.calibrateconfirm ==  False:
            self.warp = self.cont.originalimage()
        else:
            self.warp = self.cont.Warp_perspective(self.cont.pts1, self.cont.originalimage())
        self.warp = cv2.cvtColor(self.warp, cv2.COLOR_BGR2RGB)
        self.warp = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.warp))
        self.canvas.create_image(2, 2,image = self.warp, anchor = 'nw')
        if self.calibrateimagedone == False:
            self.Warp_Calibration_image()


        self.after(self.cont.delay, self.update_canvas)

    def mouse_callback(self,event, x, y, flags, params):
        if event == 2:
            global right_clicks
            right_clicks = []
            right_clicks.append([x, y])
            self.x_val = right_clicks[0][0]
            self.y_val = right_clicks[0][1]




    def Warp_Calibration_image(self):
        self.calibrateimagedone = False
        self.imgcalib = self.cont.originalimage()
        cv2.setMouseCallback("Warp_calibration_window", self.mouse_callback)
        cv2.circle(self.imgcalib, (self.x_val,self.y_val), 5,(0,255,0),-1)
        cv2.putText(self.imgcalib,'{}'.format((self.x_val,self.y_val)),(320, 50),cv2.FONT_HERSHEY_COMPLEX_SMALL,1.6,(0,255,0),2)
        cv2.imshow("Warp_calibration_window", self.imgcalib)

        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            self.calibrateimagedone = True

    def Confirm_Calibration (self):
        #-------integer values --------


        self.x1 = int(self.x1value.get())
        self.y1 = int(self.y1value.get())
        self.x2 = int(self.x2value.get())
        self.y2 = int(self.y2value.get())
        self.x3 = int(self.x3value.get())
        self.y3 = int(self.y3value.get())
        self.x4 = int(self.x4value.get())
        self.y4 = int(self.y4value.get())
        self.cont.pts1 = [[self.x1,self.y1],[self.x2,self.y2],[self.x3,self.y3],[self.x4,self.y4]]
        self.calibrateconfirm =True


class HueSaturation(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text="Hue Saturation Value Image")
        self.label.grid(row=1, column=2)
        self.dataArray = [[],[],[]]
        self.cont = cont
        self.delay = 100
        self.save_HSV_data = False


        self.canvas = tk.Canvas(self, height=cont.height, width=cont.width*2)
        self.canvas.grid(row=2, column=1, columnspan=3)

        self.Calibration_Frame = tk.LabelFrame(self, text = "Calibration",pady = 10,padx = 10)
        self.Calibration_Frame.grid(row = 4, column = 1, columnspan = 4)


############Calibration Bar#################
        self.HueMinInt = tk.IntVar()
        self.HueMaxInt = tk.IntVar()
        self.SatMinInt = tk.IntVar()
        self.SatMaxInt = tk.IntVar()
        self.ValMinInt = tk.IntVar()
        self.ValMaxInt = tk.IntVar()

        self.HueMinSlider = tk.Scale(self.Calibration_Frame, from_=0, to = 179, length =200, orient = "horizontal", label = "Hue Min", variable = self.HueMinInt ).grid(row =1,column =1)
        self.HueMaxSlider = tk.Scale(self.Calibration_Frame, from_=0, to = 179, length =200, orient = "horizontal", label = "Hue Max", variable = self.HueMaxInt).grid(row =1,column =2)
        self.SatMinSlider = tk.Scale(self.Calibration_Frame, from_=0, to = 255, length =200, orient = "horizontal", label = "Sat. Min", variable = self.SatMinInt).grid(row =2,column =1)
        self.SatMaxSlider = tk.Scale(self.Calibration_Frame, from_=0, to = 255, length =200, orient = "horizontal", label = "Sat. Max", variable = self.SatMaxInt).grid(row =2,column =2)
        self.ValMinSlider = tk.Scale(self.Calibration_Frame, from_=0, to = 255, length =200, orient = "horizontal", label = "Val. Min", variable = self.ValMinInt).grid(row =3,column =1)
        self.ValMaxSlider = tk.Scale(self.Calibration_Frame, from_=0, to = 255, length =200, orient = "horizontal", label = "Val. Max", variable = self.ValMaxInt).grid(row =3,column =2)

        self.save_HSV_data_button = tk.Button(self.Calibration_Frame, text = "Save Data", command = lambda: self.confirm_save_data()).grid(row = 2,column = 3)
        self.updatecanvas()

    def updatecanvas(self):
        self.UpdateArray()
        self.maskimg,self.HSVouput = self.cont.HSV_Calibration(self.DataArray)
        self.HSVouput = cv2.cvtColor(self.HSVouput, cv2.COLOR_BGR2RGB)
        self.maskimg = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.maskimg))
        self.HSVouput = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.HSVouput))
        self.canvas.create_image(2,2,image = self.maskimg,anchor = 'nw')
        self.canvas.create_image(self.cont.width+2,2,image = self.HSVouput,anchor = 'nw')

        self.after(self.delay,self.updatecanvas)

    def confirm_save_data(self):
        self.save_HSV_data =True
        print("data saved!")

    def UpdateArray(self):
        self.DataArray = [[self.HueMinInt.get(),self.SatMinInt.get(),self.ValMinInt.get()],[self.HueMaxInt.get(),self.SatMaxInt.get(),self.ValMaxInt.get()]]
        if self.save_HSV_data ==True:
            self.cont.DataArray = self.DataArray
            self.save_HSV_data = False




class ContourDetection(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text="Hue Saturation Value Image")
        self.label.grid(row=1, column=2)
        self.cont = cont


        self.canvas = tk.Canvas(self, height=cont.height, width=cont.width * 2)
        self.canvas.grid(row=2, column=1, columnspan=3)

        self.Calibration_Frame = tk.LabelFrame(self, text="Canny Settings", pady=10, padx=10)
        self.Calibration_Frame.grid(row=4, column=1, columnspan=4)

        self.chVarHSV = tk.IntVar()
        self.apply_HSV_CB = tk.Checkbutton(self, text="Apply_HSV_Filtering", variable = self.chVarHSV)
        self.apply_HSV_CB.deselect()
        self.apply_HSV_CB.grid(row=3, column=4)

        self.chVarWarp = tk.IntVar()
        self.apply_Warp_CB = tk.Checkbutton(self, text="Apply_Warp", variable = self.chVarWarp)
        self.apply_Warp_CB.deselect()
        self.apply_Warp_CB.grid(row=4, column=4)

        self.update_canvas()



    def update_canvas(self):
        if self.chVarHSV.get() == 1:
            mask , self.img  = self.cont.HSV_Calibration(self.cont.DataArray)
        else:
            self.img = self.cont.originalimage()

        if self.chVarWarp.get()== 1:
            self.img  = self.cont.Warp_perspective(self.cont.pts1,img = self.img)

        self.CannyImage = self.cont.Canny(img = self.img)
        self.CannyImage1 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.CannyImage))
        self.canvas.create_image(2, 2, image=self.CannyImage1, anchor='nw')
        self.ObjDetect = self.cont.getContour(self.CannyImage,self.img)
        self.ObjDetect = cv2.cvtColor(self.ObjDetect,cv2.COLOR_BGR2RGB)
        self.ObjDetect1 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.ObjDetect))
        self.canvas.create_image(self.cont.width+2 , 2, image=self.ObjDetect1, anchor='nw')

        self.after(self.cont.delay,self.update_canvas)



app = App()
app.mainloop()
