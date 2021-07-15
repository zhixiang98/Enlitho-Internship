import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import numpy as np
import time

class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.width = 1280
        self.height = 720
        self.cap.set(3, self.width)
        self.cap.set(4, self.height)

        #------Warp-Parameters--------
        self.finalwidth = 1280
        self.finalheight = 720
        self.pt1 = [[0,0],[0,0],[0,0],[0,0]]

        #------HSV Calibration---------
        self.HSVsaved = [[0,0,0],[180,255,255]]

        #-----Canny--------------------
        self.Threshold = [50,50]
        self.Bilateral_Threshold = [100,100]

        self.min_area = 1000


        #-----Toggle--------------------
        self.Warptoggle = 0
        self.HSVtoggle = 0
        self.Bilateraltoggle = 0
        self.Dilationtoggle = 0
        self.Cannytoggle = 0
        self.Contourtoggle = 0







    def originalimage(self):
        success, img = self.cap.read()
        if success:
            return img


    def outputimg(self):
        success, self.img = self.cap.read()
        # if self.Warptoggle == 0 and self.HSVtoggle == 0 and self.Bilateraltoggle == 0 and self.Cannytoggle == 0:
        #     output = self.img
        output = self.img

        if self.Warptoggle == 1:
            pt1 = np.float32(self.pt1)
            pts2 = np.float32([[0, 0], [self.finalwidth, 0], [0, self.finalheight], [self.finalwidth, self.finalheight]])
            self.matrix = cv2.getPerspectiveTransform(pt1, pts2)
            self.warpimg = cv2.warpPerspective(self.img, self.matrix, (self.finalwidth, self.finalheight))
            output = self.warpimg

        if self.HSVtoggle == 1:
            if self.Warptoggle == 1:
                workingimg = self.warpimg
            else:
                workingimg = self.img
            self.HSVimg = cv2.cvtColor(workingimg,cv2.COLOR_BGR2HSV)
            lower = np.array(self.HSVsaved[0])
            upper = np.array(self.HSVsaved[1])
            self.mask = cv2.inRange(self.HSVimg,lower,upper)
            self.HSVimg = cv2.bitwise_and(workingimg,workingimg,mask = self.mask)
            output = self.HSVimg
            # print(self.HSVsaved)
            # cv2.imshow("mask",self.mask)

        if self.Cannytoggle ==1:
            if self.HSVtoggle == 1:
                workingimg = self.HSVimg
            elif self.Warptoggle == 1:
                workingimg = self.warpimg
            else:
                workingimg = self.img
            imgGray = cv2.cvtColor(workingimg,cv2.COLOR_BGR2GRAY)
            imgGray = cv2.GaussianBlur(imgGray,(5,5),1)
            self.Canny = cv2.Canny(imgGray,self.Threshold[0],self.Threshold[1])
            if self.Bilateraltoggle == 1:
                self.Canny = cv2.bilateralFilter(imgGray,7,self.Bilateral_Threshold[0],self.Bilateral_Threshold[1])
                self.Canny = cv2.Canny(self.Canny,self.Threshold[0],self.Threshold[1])
            if self.Dilationtoggle == 1:
                imgBlank = np.ones((5,5))
                dilateimg = cv2.dilate(self.Canny,imgBlank,iterations= 2)
                self.Canny = cv2.erode(dilateimg,imgBlank,iterations = 1)
            output = self.Canny
            if self.Contourtoggle == 1:
                contours, hierarchy = cv2.findContours(self.Canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                coordinate = []
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if area > self.min_area:
                        cv2.drawContours(workingimg, cnt, -1, (255, 0, 0), 3)
                    output = workingimg
        elif (self.Bilateraltoggle == 1 or self.Dilationtoggle == 1 or self.Contourtoggle ==1) and self.Cannytoggle == 0  and self.Warptoggle == 0 and self.HSVtoggle == 0:
            pass



        return output




class App(tk.Tk,Camera):
    def __init__(self):
        tk.Tk. __init__(self)
        Camera. __init__(self)
        self.delay = 50

        container = tk.Frame(self)
        container.pack(side = 'top',fill='both', expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (Overview,Stage):
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = 'nsew')

        ##Show Menu bar###
        self.mymenu = tk.Menu(self)
        self.config(menu=self.mymenu)
        CameraCalibration = tk.Menu(self.mymenu)
        LinearStage = tk.Menu(self.mymenu)

        self.mymenu.add_cascade(label="Camera", menu=CameraCalibration)
        self.mymenu.add_cascade(label="LinearStage", menu=LinearStage)
        CameraCalibration.add_command(label="Original Image", command=lambda: self.show_frame(OriginalView))
        CameraCalibration.add_command(label="WarpPerspective", command=lambda: self.show_frame(WarpPerspective))
        CameraCalibration.add_command(label="HSVCalibration", command=lambda: self.show_frame(HueSaturation))
        CameraCalibration.add_command(label="ContourDetection", command=lambda: self.show_frame(ContourDetection))

        self.show_frame(Overview)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class Overview(tk.Frame):

    def __init__(self,parent,cont):
        tk.Frame.__init__(self,parent)
        self.cont = cont
        self.canvas = tk.Canvas(self, height=cont.height, width=cont.width, bd=None)
        self.canvas.grid(row=1, column=1,rowspan = 10)
        self.mainboundingframe = tk.LabelFrame(self, text = "Configurations")
        self.mainboundingframe.grid(row = 1,column = 2)



#-------------------OverviewCheckBoxes-----------------------------
        self.mainCBframe =tk.LabelFrame(self.mainboundingframe,text="CheckBoxes",pady = 10,padx = 10)
        self.mainCBframe.grid(row =0, column =1,sticky ='W')

        #-----------CB Variables-----------------------------------
        self.WarpCBVar = tk.IntVar()
        self.HSVCBVar = tk.IntVar()
        self.BilatCBVar = tk.IntVar()
        self.DilateCBVar = tk.IntVar()
        self.CannyCBVar = tk.IntVar()

        self.ContourDetectionCBVar = tk.IntVar()

        #----------CB Creation ------------------------------------
        self.WarpCB = tk.Checkbutton(self.mainCBframe,text = "Warp",variable =self.WarpCBVar).grid(row = 1, column =1,sticky = "nw")
        self.HSVCB = tk.Checkbutton(self.mainCBframe, text = "HSV", variable = self.HSVCBVar).grid(row = 1, column =2, sticky = "nw")
        self.CannyCB = tk.Checkbutton(self.mainCBframe,text = "Canny", variable =self.CannyCBVar).grid(row = 1, column =3,sticky= "nw")
        self.BilatCB = tk.Checkbutton(self.mainCBframe, text="Bilat", variable=self.BilatCBVar).grid(row=2, column=1, sticky = "nw")
        self.DilateCB = tk.Checkbutton(self.mainCBframe, text="Dilate", variable=self.DilateCBVar).grid(row=2, column=2, sticky = "nw")

        self.ContourDetectionCB = tk.Checkbutton(self.mainCBframe, text="Contour Detection", variable=self.ContourDetectionCBVar).grid(row=2, column=3,sticky = 'nw')

#--------------------WarpPerspective------------------------------------------------------

        #-------WarpPerspective Bounding Box ----------------
        self.entryboxframe = tk.LabelFrame(self.mainboundingframe, text="Warp Perspective", pady=10, padx=10)
        self.entryboxframe.grid(row=1, column=1,sticky ="WE")
        self.calibrateconfirm = False
        self.calibrateimagedone = True


        # -------Warp Coordinates tkinter values -----------
        self.x1coordinate = tk.IntVar()
        self.y1coordinate = tk.IntVar()
        self.x2coordinate = tk.IntVar()
        self.y2coordinate = tk.IntVar()
        self.x3coordinate = tk.IntVar()
        self.y3coordinate = tk.IntVar()
        self.x4coordinate = tk.IntVar()
        self.y4coordinate = tk.IntVar()

        #--------Warp coordinate values for Image Calibration-----------
        self.x_val = 0
        self.y_val = 0

        #-------- Warp Labels -------------------------------------------
        self.label1x = tk.Label(self.entryboxframe, text="X1:")
        self.label1x.grid(row=3, column=1, sticky="SE")
        self.label1y = tk.Label(self.entryboxframe, text="Y1:")
        self.label1y.grid(row=3, column=3, sticky="NW")
        self.x1value = tk.Entry(self.entryboxframe, width=5, textvariable=self.x1coordinate)
        self.x1value.grid(row=3, column=2, sticky="NW")
        self.y1value = tk.Entry(self.entryboxframe, width=5, textvariable=self.y1coordinate)
        self.y1value.grid(row=3, column=4, sticky="NW")

        #--------- Warp EntryBox --------------------------------------------
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

        #------------Calibration Image Button, Confirm Button, Original Image Button ---------------------
        self.calibrationbutton = tk.Button(self.entryboxframe, text="Calibration Image",command=lambda: self.Warp_Calibration_image())
        self.calibrationbutton.grid(row=3, column=5,sticky = "W")
        self.confirmbutton = tk.Button(self.entryboxframe, text="Confirm Calibration", command=lambda: self.Confirm_Calibration())
        self.confirmbutton.grid(row=4, column=5, sticky = "W")

#----------------------------HueSaturationValue----------------------------------------------------
        # -------HueSaturationValue Bounding Box ----------------
        self.HSV_Calibration_Frame = tk.LabelFrame(self.mainboundingframe, text="Hue Saturation Value")
        self.HSV_Calibration_Frame.grid(row=2, column=1, sticky = "WE")

        # ------ HSV tkinter values ------------------------------
        self.HueMinInt = tk.IntVar()
        self.HueMaxInt = tk.IntVar()
        self.SatMinInt = tk.IntVar()
        self.SatMaxInt = tk.IntVar()
        self.ValMinInt = tk.IntVar()
        self.ValMaxInt = tk.IntVar()

        # ------ HSV tkinter slider --------------------------------
        self.HueMinSlider = tk.Scale(self.HSV_Calibration_Frame, from_=0, to=179, length=100, orient="horizontal",
                                     label="Hue Min", variable=self.HueMinInt).grid(row=0, column=1)
        self.HueMaxSlider = tk.Scale(self.HSV_Calibration_Frame, from_=0, to=179, length=100, orient="horizontal",
                                     label="Hue Max", variable=self.HueMaxInt).grid(row=0, column=2)
        self.SatMinSlider = tk.Scale(self.HSV_Calibration_Frame, from_=0, to=255, length=100, orient="horizontal",
                                     label="Sat. Min", variable=self.SatMinInt).grid(row=1, column=1)
        self.SatMaxSlider = tk.Scale(self.HSV_Calibration_Frame, from_=0, to=255, length=100, orient="horizontal",
                                     label="Sat. Max", variable=self.SatMaxInt).grid(row=1, column=2)
        self.ValMinSlider = tk.Scale(self.HSV_Calibration_Frame, from_=0, to=255, length=100, orient="horizontal",
                                     label="Val. Min", variable=self.ValMinInt).grid(row=2, column=1)
        self.ValMaxSlider = tk.Scale(self.HSV_Calibration_Frame, from_=0, to=255, length=100, orient="horizontal",
                                     label="Val. Max", variable=self.ValMaxInt).grid(row=2, column=2)

        #------ HSV Confirm Button -------------------------------------
        self.colorpicker_button = tk.Button(self.HSV_Calibration_Frame, text="Color_Picker",
                                              command=lambda: self.colorpicker_calibration()).grid(row=4, column=1)


#--------------------------Canny, Bilateral Filtering --------------------------------
        self.Canny_Frame = tk.LabelFrame(self.mainboundingframe, text="Canny")
        self.Canny_Frame.grid(row=3, column=1, sticky="WE")

        #---------------Canny Threshold Variables -------------------------------
        self.minThrVar = tk.IntVar()
        self.maxThrVar = tk.IntVar()
        #-------------- Bilateral Filtering Variables ----------------------------
        self.minBilatThrVar = tk.IntVar()
        self.maxBilatThrVar = tk.IntVar()

        #---------------Canny, Bilateral THreshold Scale Bar ---------------------
        self.minThrScale = tk.Scale(self.Canny_Frame, from_=0, to=200, length=100, orient="horizontal", label="Threshold Min.", variable=self.minThrVar).grid(row=1, column=1)
        self.maxThrScale = tk.Scale(self.Canny_Frame, from_=0, to=200, length=100, orient="horizontal", label="Threshold Max.", variable=self.maxThrVar).grid(row=1, column=2)
        self.minBilatThr = tk.Scale(self.Canny_Frame, from_=0, to=1000, length=100, orient="horizontal", label="Bilat Filter Min.", variable=self.minBilatThrVar).grid(row=2, column=1)
        self.maxBilatThr = tk.Scale(self.Canny_Frame, from_=0, to=1000, length=100, orient="horizontal", label="Bilat Filter Max.", variable=self.maxBilatThrVar).grid(row=2, column=2)

# --------------------Contour Detection ---------------------------------------
        #---------------Contour Frame -----------------------------------------
        self.ContourDetection_Frame = tk.LabelFrame(self.mainboundingframe,text = "Contour Detection")
        self.ContourDetection_Frame.grid(row=4, column=1, sticky="WE")
        #--------------Contour Area Variable ----------------------------------
        self.AreaVar = tk.IntVar()
        self.AreaScale = tk.Scale(self.ContourDetection_Frame, from_=0, to=10000,length=100, orient="horizontal", label="Area", variable=self.AreaVar).grid(row=1, column=1)

#--------------------------- Main Update Canvas Function -----------------------------
        self.update_canvas()


#-------------------------------Start of Checkboxes functions -------------------------
    def updatemainCB(self):
        self.cont.Warptoggle = self.WarpCBVar.get()
        self.cont.HSVtoggle = self.HSVCBVar.get()
        self.cont.Bilateraltoggle = self.BilatCBVar.get()
        self.cont.Dilationtoggle = self.DilateCBVar.get()
        self.cont.Cannytoggle = self.CannyCBVar.get()
        self.cont.Contourtoggle = self.ContourDetectionCBVar.get()

#--------------------------------Start of Warp Perspective Functions ------------------
        # -------opens up open cv window for warp image calibration -----------

    def mouse_callback(self,event, x, y, flags, params): #mouse events that follows after right clicks
        if event == 2:
            global right_clicks
            right_clicks = []
            right_clicks.append([x, y])
            self.x_val = right_clicks[0][0]
            self.y_val = right_clicks[0][1]


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
        self.calibrateconfirm =True


    def Warp_Calibration_image(self):
        self.calibrateimagedone = False
        self.imgcalib = self.cont.originalimage()
        cv2.setMouseCallback("Warp_calibration_window", self.mouse_callback)
        cv2.circle(self.imgcalib, (self.x_val, self.y_val), 5, (0, 255, 0), -1)
        cv2.putText(self.imgcalib, '{}'.format((self.x_val, self.y_val)), (320, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.6, (0, 255, 0), 2)
        cv2.imshow("Warp_calibration_window", self.imgcalib)

        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            self.calibrateimagedone = True
#---------------------------End of Warp Perspective Functions -------------------

#---------------------------Start of HSV Calibration Functions ----------------------------

    def update_HSV_data(self):
        self.cont.HSVsaved = [[self.HueMinInt.get(),self.SatMinInt.get(),self.ValMinInt.get()],[self.HueMaxInt.get(),self.SatMaxInt.get(),self.ValMaxInt.get()]]
        # cv2.imshow("mask",self.cont.mask)
        # cv2.imshow("output",self.cont.HSVimg)

    def colorpicker_calibration(self):
        pass

# ---------------------------End of HSV Calibration Functions --------------------------

# ---------------------------Start of Canny Calibration Functions -----------------------

    def update_canny_data(self):
        self.cont.Threshold = [self.minThrVar.get(),self.maxThrVar.get()]
        self.cont.Bilateral_Threshold = [self.minBilatThrVar.get(),self.maxBilatThrVar.get()]

# --------------------------- End of Canny Calibration Functions -------------------------

#-----------------------------Start of Contour Detection Functions ------------------------
    def update_contour_data(self):
        self.cont.min_area = self.AreaVar.get()


#-------------------------Main Update Function ----------------------------------
    def update_canvas(self):


        #----------Update and check main CB --------------
        self.updatemainCB()

        #-------------Warp Calibration -------------------
        if self.calibrateconfirm == True and self.cont.Warptoggle == 1:
            self.cont.pt1 = [[self.x1, self.y1], [self.x2, self.y2], [self.x3, self.y3], [self.x4, self.y4]]
            self.calibrateconfirm = False
        if self.calibrateimagedone == False:
            self.Warp_Calibration_image()

        # ------------Hue Saturation -----------------------
        self.update_HSV_data()

        # ------------Canny----------------------------------
        self.update_canny_data()

        # ------------Contour -------------------------------
        self.update_contour_data()


        # ------------Displaying on canvas -------------------
        self.img = self.cont.outputimg()
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        self.img = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.img))
        self.canvas.create_image(2, 2, image=self.img, anchor=tk.NW)
        self.after(self.cont.delay, self.update_canvas)






class Stage (tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.cont = cont
        self.canvas1 = tk.Canvas(self, height=cont.height, width=cont.width, bg="red", bd=None)
        self.canvas1.grid(row=1, column=1)


app = App()
app.mainloop()
