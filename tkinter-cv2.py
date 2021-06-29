import tkinter
import cv2
import PIL.Image, PIL.ImageTk


class MyVideoCapture:

    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unableto open video source", video_source)

        # get video source width and height
        self.width = self.vid.get((cv2.CAP_PROP_FRAME_WIDTH))
        self.height = self.vid.get((cv2.CAP_PROP_FRAME_HEIGHT))

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.mymenu = tkinter.Menu(self.window)
        self.window.config(menu= self.mymenu)
        self.delay = 15  # delay for update set in milliseconds

        # Create a menu bar
        file_menu = tkinter.Menu(self.mymenu)
        self.mymenu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.file_new)
        file_menu.add_command(label="Exit", command=self.window.quit)

        # Create a new frame
        self.file_new_frame = tkinter.Frame(self.window,width = 400,height = 400,bg = "red")

        # open video source
        self.vid = MyVideoCapture(video_source)

        # Create a canvas that fit above video source size
        self.canvas = tkinter.Canvas(window, width=self.vid.width, height=self.vid.height * 2)
        self.canvas.pack()
        self.update()

        self.window.mainloop()

    def update(self):
        # Get a frame from video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)

        self.window.after(self.delay, self.update)

    def hide_all_frames(self):
        self.canvas.pack_forget()
        self.file_new_frame.pack_forget()

    def file_new(self):
        self.hide_all_frames()
        self.file_new_frame.pack(fill = 'both', expand =1)



App(tkinter.Tk(), "Tkinter and OpenCV")

