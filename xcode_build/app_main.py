#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys
try:
    from tkinter import *
except ImportError:  #Python 2.x
    PythonVersion = 2
    from Tkinter import *
    from tkFont import Font
    from ttk import *
    #Usage:showinfo/warning/error,askquestion/okcancel/yesno/retrycancel
    from tkMessageBox import *
    #Usage:f=tkFileDialog.askopenfilename(initialdir='E:/Python')
    #import tkFileDialog
    #import tkSimpleDialog
else:  #Python 3.x
    PythonVersion = 3
    from tkinter.font import Font
    from tkinter.ttk import *
    from tkinter.messagebox import *
    #import tkinter.filedialog as tkFileDialog
    #import tkinter.simpledialog as tkSimpleDialog    #askstring()

class Application_ui(Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('Form1')
        self.master.geometry('687x446')
        self.createWidgets()

    def createWidgets(self):
        self.top = self.winfo_toplevel()

        self.style = Style()

        self.Combo1List = ['Add items in design or code!',]
        self.Combo1 = Combobox(self.top, values=self.Combo1List, font=('宋体',9))
        self.Combo1.place(relx=0.023, rely=0.036, relwidth=0.421, relheight=0.045)
        self.Combo1.set(self.Combo1List[0])

        self.Combo2List = ['Add items in design or code!',]
        self.Combo2 = Combobox(self.top, values=self.Combo2List, font=('宋体',9))
        self.Combo2.place(relx=0.012, rely=0.108, relwidth=0.432, relheight=0.045)
        self.Combo2.set(self.Combo2List[0])

        self.List1Var = StringVar(value='List1')
        self.List1Font = Font(font=('宋体',9))
        self.List1 = Listbox(self.top, listvariable=self.List1Var, font=self.List1Font)
        self.List1.place(relx=0.023, rely=0.197, relwidth=0.432, relheight=0.224)

        self.style.configure('Command1.TButton',font=('宋体',9))
        self.Command1 = Button(self.top, text='Command1', command=self.Command1_Cmd, style='Command1.TButton')
        self.Command1.place(relx=0.023, rely=0.484, relwidth=0.409, relheight=0.074)

        self.style.configure('Command2.TButton',font=('宋体',9))
        self.Command2 = Button(self.top, text='Command2', command=self.Command2_Cmd, style='Command2.TButton')
        self.Command2.place(relx=0.023, rely=0.61, relwidth=0.421, relheight=0.074)

        self.style.configure('Command3.TButton',font=('宋体',9))
        self.Command3 = Button(self.top, text='Command3', command=self.Command3_Cmd, style='Command3.TButton')
        self.Command3.place(relx=0.023, rely=0.717, relwidth=0.421, relheight=0.074)

        self.style.configure('Command4.TButton',font=('宋体',9))
        self.Command4 = Button(self.top, text='Command4', command=self.Command4_Cmd, style='Command4.TButton')
        self.Command4.place(relx=0.023, rely=0.825, relwidth=0.421, relheight=0.074)

        self.style.configure('Command5.TButton',font=('宋体',9))
        self.Command5 = Button(self.top, text='Command5', command=self.Command5_Cmd, style='Command5.TButton')
        self.Command5.place(relx=0.023, rely=0.915, relwidth=0.421, relheight=0.074)


class Application(Application_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
    def __init__(self, master=None):
        Application_ui.__init__(self, master)

    def Command1_Cmd(self, event=None):
        #TODO, Please finish the function here!
        pass

    def Command2_Cmd(self, event=None):
        #TODO, Please finish the function here!
        pass

    def Command3_Cmd(self, event=None):
        #TODO, Please finish the function here!
        pass

    def Command4_Cmd(self, event=None):
        #TODO, Please finish the function here!
        pass

    def Command5_Cmd(self, event=None):
        #TODO, Please finish the function here!
        pass

if __name__ == "__main__":
    top = Tk()
    Application(top).mainloop()
    try: top.destroy()
    except: pass
