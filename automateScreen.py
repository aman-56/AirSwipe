import pyautogui as pag
import pygetwindow as pgw
import os
import handDetectorModule as hDM


class ScreenController:

    @staticmethod
    def system_sleep():
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        hDM.GestureRecognitions.run = False

    @staticmethod
    def change_workspace(option):
        # print("change workspace",option)
        if option == "New":
            pag.hotkey('win', 'ctrl', 'd')
        elif option == "Left":
            pag.hotkey('win', 'ctrl', 'left')
            ScreenController.change = True
        elif option == "Right":
            pag.hotkey('win', 'ctrl', 'right')
            ScreenController.change = True
        elif option == "Close":
            pag.hotkey('ctrl', 'win', 'f4')
            ScreenController.change = True

    @staticmethod
    def change_windows(scobj, option):
        if option == "Close":
            pag.hotkey('alt', 'F4')
        elif option == "Left" or option == "Right":
            pag.keyDown('alt')
            completed = scobj.check_further_change()
            if completed:
                pag.keyUp('alt')
        elif option == "Minimize":
            if pgw.getActiveWindow().title() != "":
                pgw.getActiveWindow().minimize()
