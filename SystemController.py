# --------------------------------------------------------------------------------------------------------------
# -- Title      : Robot and Platform controller
# -- File       : SystemController.vhd
# -- Purpose    : Creates the GUI of the application. With this GUI the user can control the mBit Robot by sending
# --              movement commands (with various ways) and also turn on and off the platform lights (traffic and led).
# --              The commands are sent through the serial port utilizing a second mBit as a transmitter.
# --              The platform lights are switch on/off by invoking/killing processes using the python files
# --              "traffic_lights.py"/"traffic_lights_off.py" and "lights.py"/"lights_off.py".
# -- Notes      : The serial cable with the transmitter mBit must be connected to the system prior of the
# --              execution, or errors will be generated.
# --              The lights of the platform (traffic and led) can be controlled only if the execution is
# --              on the Raspberry Pi used for the control of the lights.
# --              This script can be used also in Windows just for transmitting the command to the mBit Robot.
# --              The step size of the Robot can be set in the tab 'Συντελεστές κίνησης'.
# --              In the first window that opens prior the execution of the application, the user must enter
# --              the correct serial communication port and select the appropriate OS.
# --------------------------------------------------------------------------------------------------------------
# -- Author     : Ioannis Stamoulias  <istamoulias@gmail.com>
# -- Created    : 2021-05-11
# -- Last update: 2021-06-13
# -- Platform   : Developed for Raspberry Pi OS, limited support for Windows 10.
# --              The processes for the traffic lights and the lights of the platform are
# --              supported only in Raspberry Pi OS (use of RPi.GPIO library).
# -- Standard   : Python 3
# --------------------------------------------------------------------------------------------------------------
# -- Copyright (c) 2021
# --------------------------------------------------------------------------------------------------------------

# import sys  # Used during debug for starting processes in Windows OS
import os
import signal
from tkinter import *
import tkinter.messagebox
import tkinter as tk
from tkinter import ttk
import serial
from subprocess import Popen

# Variables used as temp for the processes and the sizes of the steps
tr_poc_run = 0
lg_poc_run = 0
file_r = open("./settings/fb_factor.dat", "r")
fb_txt_value = file_r.read()
file_r.close()
file_r = open("./settings/lr_factor.dat", "r")
lr_txt_value = file_r.read()
file_r.close()
# At the start it request the type of OS for opening the correct serial port
# Change the default value at the text box if necessary and then press the button


def raspberry_os():  # When Raspberry OS is selected
    global os_used
    global os_select
    box_rasp_value = txt_rasp.get()
    os_used = box_rasp_value
    os_select = 0
    # print("Rasp")
    var.set(1)


def windows_os():  # When Windows OS is selected
    global os_used
    global os_select
    box_win_value = txt_win.get()
    os_used = box_win_value
    os_select = 1
    # print("Win")
    var.set(1)


# Creates the first window for selecting the OS
SelectOSserial = False
if not SelectOSserial:
    SelectOSserial = True
    win = tk.Tk()
    win.title("Επιλογή Λειτουργικού")
    rasp_img = PhotoImage(file='./images/Raspberry.png')
    rasp_img2 = rasp_img.subsample(2, 2)
    win_img = PhotoImage(file='./images/Windows.png')
    win_img2 = win_img.subsample(2, 2)
    var = tk.IntVar()
    empty_start = Label(win, text="   ", font=("Arial Bold", 12))
    empty_start.grid(column=0, row=0)
    btn_rasp = Button(win, image=rasp_img2, command=raspberry_os)
    btn_rasp.grid(column=1, row=1)
    empty_row = Label(win, text="   ", font=("Arial Bold", 12))
    empty_row.grid(column=1, row=2)
    txt_rasp = Entry(win, width=12, fg="DeepPink2")
    txt_rasp.insert(0, '/dev/ttyACM0')
    txt_rasp.grid(column=1, row=3)
    empty_clmn = Label(win, text="   ", font=("Arial Bold", 12))
    empty_clmn.grid(column=2, row=1)
    btn_win = Button(win, image=win_img2, command=windows_os)
    btn_win.grid(column=3, row=1)
    txt_win = Entry(win, width=12, fg="blue")
    txt_win.insert(0, 'COM8')
    txt_win.grid(column=3, row=3)
    empty_row2 = Label(win, text="   ", font=("Arial Bold", 12))
    empty_row2.grid(column=4, row=4)
    win.wait_variable(var)
    win.destroy()

# Creates and opens the serial link for sending commands through the mBit transmitter
try:
    global serialPort
    serialPort = serial.Serial(port=os_used, baudrate=115200, bytesize=8,
                               parity=serial.PARITY_NONE, timeout=2,
                               stopbits=serial.STOPBITS_ONE)
except serial.serialutil.SerialException:
    tkinter.messagebox.showinfo("Πρόβλημα στην συνδεσμολογία", "Δεν είναι συνδεδεμένο το mBit για την αποστολή εντολών")
    # print("Δεν είναι συνδεδεμένο το mBit για την αποστολή εντολών")
    sys.exit(0)

if serialPort.isOpen():
    serialPort.close()
serialPort.open()

# Creates the main window of the application
window = tk.Tk()
window.title("Άκη Ρομποτάκι σε αγαπάμε…")
# window.geometry('720x480')  # We avoid to have a fixed size, so it set it based on the content
tabControl = ttk.Notebook(window, takefocus=NO)
window.configure(background='black')
# --------------------------------------------------------------------------------------------------------------
# Code for the first tab (type of movement and number of steps)


def clicked():  # Stores and transmits the user's values through the serial port
    # The value for the orientation of the movement
    select_value = selected.get()
    if select_value == 1:
        slct_vl = 'F'
    elif select_value == 2:
        slct_vl = 'B'
    elif select_value == 3:
        slct_vl = 'L'
    elif select_value == 4:
        slct_vl = 'R'
    else:
        slct_vl = 'S'
    # The value for the number of steps, in every case we also consider the factor for the steps
    #  that was set in the 'Συντελεστές κίνησης' tab
    box_value = txt.get()
    if select_value == 1 or select_value == 2:
        factored_box_value = int(box_value)*int(fb_txt_value)
    else:
        factored_box_value = int(box_value)*int(lr_txt_value)
    check = box_value.isnumeric()
    if check == FALSE:
        tkinter.messagebox.showinfo('Μη έγκυρη τιμή', 'Στο πεδίο \"Βήματα\" πρέπει να δώσετε αριθμό')
    else:
        # Prepares and sends the command through the serial port
        serial_string = slct_vl + str(factored_box_value) + "\r\n"
        if tabControl.tab(tabControl.select(), "text") == 'Εφαρμογή':
            serialPort.write(serial_string.encode())


tab1 = ttk.Frame(tabControl, takefocus=NO)
tabControl.add(tab1, text='Εφαρμογή')
lbl_empty = Label(tab1, text="   ", fg="cyan4", font=("Arial Bold", 24))
lbl_empty.grid(column=0, row=0)
lbl = Label(tab1, text="Άκης Ρομποτάκης: ", fg="cyan4", font=("Arial Bold", 12))
lbl_0 = Label(tab1, text="Που να πάω; ", fg="maroon4", font=("Arial Bold", 12))
lbl.focus_force()
lbl.grid(column=1, row=1)
lbl_0.grid(column=2, row=1)
lb2_empty = Label(tab1, text="   ", fg="cyan4", font=("Arial Bold", 12))
lb2_empty.grid(column=0, row=2)
lb2 = Label(tab1, text="Παιδάκι: ", fg="lime green", font=("Arial Bold", 12))
lb2.grid(column=1, row=4)
lb2_0 = Label(tab1, text="Πήγαινε ", fg="DeepPink2", font=("Arial Bold", 12))
lb2_0.grid(column=2, row=4)
selected = IntVar()
rad1 = Radiobutton(tab1, text='Μπροστά', fg="forest green", font=("Arial Bold", 12), value=1, variable=selected)
rad1.grid(column=4, row=3)
rad2 = Radiobutton(tab1, text='Πίσω       ', fg="indian red", font=("Arial Bold", 12), value=2, variable=selected)
rad2.grid(column=4, row=5)
rad3 = Radiobutton(tab1, text='Αριστερά', fg="tomato", font=("Arial Bold", 12), value=3, variable=selected)
rad3.grid(column=3, row=4)
rad4 = Radiobutton(tab1, text='Δεξιά', fg="slate blue", font=("Arial Bold", 12), value=4, variable=selected)
rad4.grid(column=5, row=4)
lb3_empty = Label(tab1, text="   ", fg="cyan4", font=("Arial Bold", 12))
lb3_empty.grid(column=0, row=6)
lb3 = Label(tab1, text="Άκης Ρομποτάκης: ", fg="cyan4", font=("Arial Bold", 12))
lb3_0 = Label(tab1, text="Πόσα βήματα", fg="dark orange", font=("Arial Bold", 12))
lb3_1 = Label(tab1, text="να κάνω;", fg="dark orange", font=("Arial Bold", 12))
lb3.grid(column=1, row=7)
lb3_0.grid(column=2, row=7)
lb3_1.grid(column=3, row=7)
lb4_empty = Label(tab1, text="   ", fg="cyan4", font=("Arial Bold", 12))
lb4_empty.grid(column=0, row=8)
lb4 = Label(tab1, text="Παιδάκι: ", fg="lime green", font=("Arial Bold", 12))
lb4.grid(column=1, row=9)
lb4_0 = Label(tab1, text="Κάνε ", fg="purple3", font=("Arial Bold", 12))
lb4_0.grid(column=2, row=9)
txt = Entry(tab1, width=10, fg="purple3")
txt.grid(column=3, row=9)
lb4_1 = Label(tab1, text="βήματα", fg="purple3", font=("Arial Bold", 12))
lb4_1.grid(column=4, row=9)
lb5_empty = Label(tab1, text="   ", fg="cyan4", font=("Arial Bold", 12))
lb5_empty.grid(column=0, row=10)
lb5 = Label(tab1, text="Άκης Ρομποτάκης:", fg="cyan4", font=("Arial Bold", 12))
lb5_0 = Label(tab1, text="Να ξεκινήσω;", fg="yellow3", font=("Arial Bold", 12))
lb5.grid(column=1, row=11)
lb5_0.grid(column=2, row=11)
lb6_empty = Label(tab1, text="   ", fg="cyan4", font=("Arial Bold", 12))
lb6_empty.grid(column=0, row=12)
lb6 = Label(tab1, text="Παιδάκι: ", fg="lime green", font=("Arial Bold", 12))
lb6.grid(column=1, row=13)
btn2 = Button(tab1, text="Ναι", fg="RoyalBlue3", command=clicked)
btn2.grid(column=2, row=13)
# --------------------------------------------------------------------------------------------------------------
# Code for the second tab (movement using the arrow keys)
# From this tab the user can only move the robot one step at a time, so we transmit
# just the movement factor that was set in 'Συντελεστές κίνησης' tab


def key(event):  # Reads key presses and prepares and sends the movement commands
    if tabControl.tab(tabControl.select(), "text") == 'Πληκτρολόγιο':
        if event.keysym == 'Up':
            slct_vl = 'F'
            box_value = fb_txt_value
            serial_string = slct_vl + box_value + "\r\n"
            serialPort.write(serial_string.encode())
        elif event.keysym == 'Down':
            slct_vl = 'B'
            box_value = fb_txt_value
            serial_string = slct_vl + box_value + "\r\n"
            serialPort.write(serial_string.encode())
        elif event.keysym == 'Left':
            slct_vl = 'L'
            box_value = lr_txt_value
            serial_string = slct_vl + box_value + "\r\n"
            serialPort.write(serial_string.encode())
        elif event.keysym == 'Right':
            slct_vl = 'R'
            box_value = lr_txt_value
            serial_string = slct_vl + box_value + "\r\n"
            serialPort.write(serial_string.encode())
        elif event.keysym == 'Escape':
            tab1.destroy()
            tab2.destroy()
            if os_select == 0:
                tab3.destroy()
            tab4.destroy()
            serialPort.close()
            if tr_poc_run == 1:
                os.kill(traffic_pid, 9)
            if lg_poc_run == 1:
                os.kill(light_pid, 9)
            Popen(['python3', './scripts/traffic_lights_off.py'])
            Popen(['python3', './scripts/lights_off.py'])
            window.destroy()
            # print('ΤΕΛΟΣ')
        else:
            tkinter.messagebox.showinfo('Text', 'Μόνο βελάκια\n''ή\n''\"esc\" για έξοδο')
    else:
        if event.keysym == 'Escape':
            tab1.destroy()
            tab2.destroy()
            if os_select == 0:
                tab3.destroy()
            tab4.destroy()
            serialPort.close()
            if tr_poc_run == 1:
                os.kill(traffic_pid, 9)
            if lg_poc_run == 1:
                os.kill(light_pid, 9)
            Popen(['python3', './scripts/traffic_lights_off.py'])
            Popen(['python3', './scripts/lights_off.py'])
            window.destroy()
            # print('ΤΕΛΟΣ')


def press_up():  # Reads the press of the up GUI button and sends the movement commands
    slct_vl = 'F'
    box_value = fb_txt_value
    serial_string = slct_vl + box_value + "\r\n"
    serialPort.write(serial_string.encode())


def press_left():  # Reads the press of the left GUI button and sends the movement commands
    slct_vl = 'L'
    box_value = lr_txt_value
    serial_string = slct_vl + box_value + "\r\n"
    serialPort.write(serial_string.encode())


def press_right():  # Reads the press of the right GUI button and sends the movement commands
    slct_vl = 'R'
    box_value = lr_txt_value
    serial_string = slct_vl + box_value + "\r\n"
    serialPort.write(serial_string.encode())


def press_down():  # Reads the press of the down GUI button and sends the movement commands
    slct_vl = 'B'
    box_value = fb_txt_value
    serial_string = slct_vl + box_value + "\r\n"
    serialPort.write(serial_string.encode())


tab2 = ttk.Frame(tabControl, takefocus=NO)
tabControl.add(tab2, text='Πληκτρολόγιο')
lb7_empty = Label(tab2, text="   ", fg="cyan4", font=("Arial Bold", 24))
lb7_empty.grid(column=0, row=0)
lb7 = Label(tab2, text="Χρησιμοποίησε τα χρωματιστά βελάκια", fg="SeaGreen3", font=("Arial Bold", 12))
lb7.focus_force()
lb7.grid(column=4, row=1)
lb7_0 = Label(tab2, text="ή τα βελάκια στο πληκτρολόγιο", fg="cadet blue", font=("Arial Bold", 12))
lb7_0.grid(column=4, row=2)
arrow_empty = Label(tab2, text="   ", fg="cyan4", font=("Arial Bold", 12))
arrow_empty.grid(column=0, row=3)
arrow_up_img = PhotoImage(file='./images/Arrow_up.png')
arrow_up = arrow_up_img.subsample(3, 3)
btn_arup = Button(tab2, image=arrow_up, command=press_up)
btn_arup.grid(column=2, row=4)
arrow_left_img = PhotoImage(file='./images/Arrow_left.png')
arrow_left = arrow_left_img.subsample(3, 3)
btn_arleft = Button(tab2, image=arrow_left, command=press_left)
btn_arleft.grid(column=1, row=5)
arrow_right_img = PhotoImage(file='./images/Arrow_right.png')
arrow_right = arrow_right_img.subsample(3, 3)
btn_arright = Button(tab2, image=arrow_right, command=press_right)
btn_arright.grid(column=3, row=5)
arrow_down_img = PhotoImage(file='./images/Arrow_down.png')
arrow_down = arrow_down_img.subsample(3, 3)
btn_ardown = Button(tab2, image=arrow_down, command=press_down)
btn_ardown.grid(column=2, row=6)
arrow2_empty = Label(tab2, text="   ", fg="cyan4", font=("Arial Bold", 12))
arrow2_empty.grid(column=0, row=7)
lb7_1 = Label(tab2, text="και όταν θελήσεις να φύγεις,", fg="pale violet red", font=("Arial Bold", 12))
lb7_1.grid(column=4, row=8)
lb7_1 = Label(tab2, text="μπορείς να πατήσεις \'esc\' στο πληκτρολόγιο", fg="SteelBlue2", font=("Arial Bold", 12))
lb7_1.grid(column=4, row=9)
lb7_1 = Label(tab2, text="ή το 'Χ' στο παράθυρο", fg="hot pink", font=("Arial Bold", 12))
lb7_1.grid(column=4, row=10)
# --------------------------------------------------------------------------------------------------------------
# Code for the third tab (lights switches)


def tr_clicked():  # When the traffic light check box is changed
    select_value = selected_traffic.get()
    global tr_poc_run
    if select_value == 1:  # Creates a new process using "traffic_lights.py"
        traffic_process = Popen(['python3', './scripts/traffic_lights.py'])
        #traffic_process = Popen([sys.executable, "./scripts/traffic_lights.py"])
        # Stores the PID for later use
        global traffic_pid
        traffic_pid = traffic_process.pid
        tr_poc_run = 1
    else:  # Kills the process with the specific PID
        os.kill(traffic_pid, 9)
        tr_poc_run = 0
        # Turn off all lights
        Popen(['python3', './scripts/traffic_lights_off.py'])


def lg_clicked():  # When the led light check box is changed
    select_value = selected_led.get()
    global lg_poc_run
    if select_value == 1:  # Creates a new process using "lights.py"
        light_process = Popen(['python3', './scripts/lights.py'])
        #light_process = Popen([sys.executable, "./scripts/traffic_lights.py"])
        # Stores the PID for later use
        global light_pid
        light_pid = light_process.pid
        lg_poc_run = 1
    else:  # Kills the process with the specific PID
        os.kill(light_pid, 9)
        lg_poc_run = 0
        # Turn off all lights
        Popen(['python3', './scripts/lights_off.py'])


if os_select == 0:  # We only create this tab, if the selected OS is Raspberry
    tab3 = ttk.Frame(tabControl, takefocus=NO)
    tabControl.add(tab3, text='Φανάρια και Φώτα')
    lb8_empty = Label(tab3, text="   ", fg="cyan4", font=("Arial Bold", 24))
    lb8_empty.grid(column=0, row=0)
    lb8 = Label(tab3, text="Ενεργοποίηση", fg="forest green", font=("Arial Bold", 12))
    lb8.grid(column=3, row=1)
    lb8_0 = Label(tab3, text=" και ", fg="bisque4", font=("Arial Bold", 12))
    lb8_0.grid(column=4, row=1)
    lb8_1 = Label(tab3, text="Απενεργοποίηση", fg="red", font=("Arial Bold", 12))
    lb8_1.grid(column=5, row=1)
    chk_empty = Label(tab3, text="   ", fg="cyan4", font=("Arial Bold", 12))
    chk_empty.grid(column=0, row=2)
    selected_traffic = IntVar()
    selected_led = IntVar()
    chk1 = Checkbutton(tab3, text="Φωτεινοί", fg="red", font=("Arial Bold", 12), variable=selected_traffic, command=tr_clicked)
    chk1.grid(column=1, row=3, sticky=W)
    chk1_0 = Label(tab3, text="Σηματοδότες", fg="orange2", font=("Arial Bold", 12))
    chk1_0.grid(column=2, row=3)
    chk1_1 = Label(tab3, text="Κυκλοφορίας", fg="forest green", font=("Arial Bold", 12))
    chk1_1.grid(column=3, row=3)
    chk_empty2 = Label(tab3, text="   ", fg="cyan4", font=("Arial Bold", 12))
    chk_empty2.grid(column=0, row=4)
    chk2 = Checkbutton(tab3, text="Φωτισμός", fg="yellow", font=("Arial Bold", 12), variable=selected_led, command=lg_clicked)
    chk2.grid(column=1, row=5, sticky=W)
# --------------------------------------------------------------------------------------------------------------
# Code for the fourth tab (step and turn factor)
# In this tab the user can adjust the movement factor of each step for forward/backward and left/right move.
# By changing these values we cn have longer or shorter steps and turn left or right in different angles.


def update_factors():
    file_w = open("./settings/fb_factor.dat", "w")
    file_w.write(value_fb.get())
    global fb_txt_value
    fb_txt_value = value_fb.get()
    file_w.close()
    file_w = open("./settings/lr_factor.dat", "w")
    file_w.write(value_lr.get())
    global lr_txt_value
    lr_txt_value = value_lr.get()
    file_w.close()


tab4 = ttk.Frame(tabControl, takefocus=NO)
tabControl.add(tab4, text='Συντελεστές κίνησης')
factor_empty = Label(tab4, text="   ", fg="cyan4", font=("Arial Bold", 24))
factor_empty.grid(column=0, row=0)
lb_factor_fb = Label(tab4, text="Καθορίζει το μήκος ενός βήματος", fg="forest green", font=("Arial Bold", 12))
lb_factor_fb.grid(column=1, row=1)
value_fb = Entry(tab4, width=12, fg="forest green")
value_fb.insert(0, fb_txt_value)
value_fb.grid(column=1, row=2)
factor_empty2 = Label(tab4, text="   ", fg="cyan4", font=("Arial Bold", 12))
factor_empty2.grid(column=0, row=3)
lb_factor_lr = Label(tab4, text="Καθορίζει την γωνία της στροφής", fg="tomato", font=("Arial Bold", 12))
lb_factor_lr.grid(column=1, row=4)
value_lr = Entry(tab4, width=12, fg="tomato")
value_lr.insert(0, lr_txt_value)
value_lr.grid(column=1, row=5)
factor_empty3 = Label(tab4, text="   ", fg="cyan4", font=("Arial Bold", 12))
factor_empty3.grid(column=0, row=6)
btn2 = Button(tab4, text="Ενημέρωση", fg="purple3", command=update_factors)
btn2.grid(column=1, row=7)
# --------------------------------------------------------------------------------------------------------------
# Code for the fifth tab (About)
tab5 = ttk.Frame(tabControl, takefocus=NO)
tabControl.add(tab5, text='Σχετικά με...')
lb9 = Label(tab5, text="3ος Πανελλήνιος ", fg="orange", font=("Arial Bold", 12))
lb9.grid(column=0, row=0, sticky=E)
lb9_0 = Label(tab5, text="Διαγωνισμός Ανοιχτών Τεχνολογιών στην Εκπαίδευση 2021", fg="DarkOrange1", font=("Arial Bold", 12))
lb9_0.grid(column=1, row=0)
lb_empty = Label(tab5, text="    ", font=("Arial Bold", 12))
lb_empty.grid(column=1, row=1)
lb10 = Label(tab5, text="Όνομα Ομάδας:", fg="RoyalBlue2", font=("Arial Bold", 11))
lb10.grid(column=0, row=2)
lb10_0 = Label(tab5, text="Νηπιαγωγείο Κάτω Τιθορέας", fg="RoyalBlue2", font=("Arial Bold", 11))
lb10_0.grid(column=1, row=2)
lb11 = Label(tab5, text="Τίτλος έργου:", fg="cyan4", font=("Arial Bold", 11))
lb11.grid(column=0, row=3)
lb11_0 = Label(tab5, text="Άκη Ρομποτάκι σε αγαπάμε....με ασφάλεια το δρόμο περνάμε.", fg="cyan4", font=("Arial Bold", 11))
lb11_0.grid(column=1, row=3)
lb12 = Label(tab5, text="Github έργου:", fg="blue2", font=("Arial Bold", 11))
lb12.grid(column=0, row=4)
lb12_0 = Label(tab5, text="https://github.com/tosxoleio-mou/-", fg="blue2", font=("Arial Bold", 10))
lb12_0.grid(column=1, row=4)
lb12_empty = Label(tab5, text="   ", fg="cyan4", font=("Arial Bold", 12))
lb12_empty.grid(column=0, row=5)
lb13 = Label(tab5, text="Εκπαιδευτικοί:", fg="SpringGreen3", font=("Arial Bold", 11))
lb13.grid(column=0, row=6)
lb13_0 = Label(tab5, text="Κατόπη Γεωργία, Κατσακιώρη Μαρίνα, Κωστή Κυριακή", fg="SpringGreen3", font=("Arial Bold", 9))
lb13_0.grid(column=1, row=6)
lb14 = Label(tab5, text="Παιδάκια: ", fg="cyan3", font=("Arial Bold", 11))
lb14.grid(column=0, row=7)
lb14_0 = Label(tab5, text="Ασλλάνι Αμέλια, Βασιλακάκος Παύλος, Γερογιάννης Θοδωρής, Γεροχρήστος Θανάσης,", fg="turquoise3", font=("Arial Bold", 9))
lb14_0.grid(column=1, row=7)
lb14_1 = Label(tab5, text="Γεωργίου Αλέξανδρος, Γιαλούρη Μαρία, Γκορρέγια Στέφανο, Δογάνης Παναγιώτης,", fg="DodgerBlue3", font=("Arial Bold", 9))
lb14_1.grid(column=1, row=8)
lb14_2 = Label(tab5, text="Θεοδώρου Γεωργία, Κακός Νέστορας, Καντάκος Σωτήρης, Καπερώνη Μάρθα, Κινιόβ Μάξιμος,", fg="deep pink", font=("Arial Bold", 9))
lb14_2.grid(column=1, row=9)
lb14_3 = Label(tab5, text="Κοζάκης Άγγελος, Κοπανάκης Κώστας, Κότσι Ανδρέας, Κουκουτσίδης Μάρκος, Κουρής Νικόλας,", fg="cornflower blue", font=("Arial Bold", 9))
lb14_3.grid(column=1, row=10)
lb14_4 = Label(tab5, text="Λάμπρου Γιάννης, Μπινιώρης Γιάννης, Ντσίμας Κωνσταντίνος, Πάλλας Γιώργος, Πόρρος Αντώνης,", fg="DeepSkyBlue3", font=("Arial Bold", 9))
lb14_4.grid(column=1, row=11)
lb14_5 = Label(tab5, text="Πρένγκα Μαρία, Σαράντης Μανώλης, Σκεντέρι Νόρα, Σταμούλια Κωνσταντινιά Αγάπη,", fg="magenta2", font=("Arial Bold", 9))
lb14_5.grid(column=1, row=12)
lb14_6 = Label(tab5, text="Τασόπουλος Πέτρος, Τζαναβέλης Κωσταντής, Φάσκο Έλιον, Χλωμίσιος Αναστάσης,", fg="steel blue", font=("Arial Bold", 9))
lb14_6.grid(column=1, row=13)
lb14_7 = Label(tab5, text="Φίνος Γιάννης, Φίνου Αθανασία, Φράγκου Σίλια, Χυσένι Φλάβιο", fg="medium sea green", font=("Arial Bold", 9))
lb14_7.grid(column=1, row=14)
lb15 = Label(tab5, text="Εξωτερικοί Συνεργάτες:", fg="SpringGreen3", font=("Arial Bold", 11))
lb15.grid(column=0, row=15)
lb15_0 = Label(tab5, text="Λεονάρδος Θοδωρής, Σταμούλιας Ιωάννης, ", fg="SpringGreen3", font=("Arial Bold", 9))
lb15_0.grid(column=1, row=15)
lb16 = Label(tab5, text=" ", font=("Arial Bold", 10))
lb16.grid(column=0, row=16)
lb17 = Label(tab5, text="Created by:", fg="dark slate gray", font=("Arial Bold", 10))
lb17.grid(column=0, row=17)
lb17_0 = Label(tab5, text="Σταμούλιας Ιωάννης <istamoulias@gmail.com>", fg="dark slate gray", font=("Arial Bold", 9))
lb17_0.grid(column=1, row=17)
# --------------------------------------------------------------------------------------------------------------


def close_program():
    serialPort.close()
    if tr_poc_run == 1:
        os.kill(traffic_pid, 9)
    if lg_poc_run == 1:
        os.kill(light_pid, 9)
    Popen(['python3', './scripts/traffic_lights_off.py'])
    Popen(['python3', './scripts/lights_off.py'])
    sys.exit(0)


signal.signal(signal.SIGINT, close_program)

tabControl.pack(expand=1, fill="both")
window.bind_all('<Key>', key)
window.mainloop()
