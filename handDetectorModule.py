import mediapipe as mp
import cv2
import pyautogui as pag
import numpy as np
import automateScreen as autoscr


class GestureRecognitions:
    run = True
    draw = True
    change = True

    def __init__(self):

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.75)
        self.mp_draw = mp.solutions.drawing_utils

        self.width, self.height = pag.size()

        self.cap = cv2.VideoCapture(0)
        self.cap.set(2, self.width)
        self.cap.set(3, self.height)
        self.img = None

        self.prev_pos = [0, 0]
        self.cur_pos = [0, 0]

        self.multi_hands = None
        self.hand = None
        self.fingers = None

    def hand_detection_from_image(self):
        self.multi_hands = None
        self.img = None
        ret, self.img = self.cap.read()
        if not ret:
            return
        self.img = cv2.flip(cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB), 1)

        # Processes an RGB image and returns the hand landmarks and handedness of each detected hand
        self.multi_hands = self.hands.process(self.img).multi_hand_landmarks

    def hand_detection(self):

        try:
            while GestureRecognitions.run:

                self.hand_detection_from_image()
                if self.multi_hands:

                    if self.is_two_hands():
                        self.two_hand_gesture()
                    else:
                        if GestureRecognitions.change:
                            self.hand = self.multi_hands[0]
                            self.update_hand_pos()
                        self.one_hand_gesture()

                    if self.draw:
                        for one_hand_lms in self.multi_hands:
                            self.mp_draw.draw_landmarks(self.img, one_hand_lms, self.mp_hands.HAND_CONNECTIONS)

                cv2.waitKey(1)
                cv2.imshow("Detecting Screen", self.img)

        finally:
            pag.keyUp('alt')
            self.cap.release()

    def is_two_hands(self):
        if len(self.multi_hands) == 2:
            return True

        return False

    def two_hand_gesture(self):

        self.hand = self.multi_hands[0]
        hand1_center = self.mean_finder()
        finger_hand1 = self.count_open_fingers()

        self.hand = self.multi_hands[1]
        hand2_center = self.mean_finder()
        finger_hand2 = self.count_open_fingers()

        dist = np.linalg.norm(hand1_center - hand2_center)

        if 350 < dist < 400 and finger_hand1.count(1) == 5 and finger_hand2.count(1) == 5:
            autoscr.ScreenController.system_sleep()

    def one_hand_gesture(self):

        self.hand = self.multi_hands[0]
        self.fingers = self.count_open_fingers()
        self.cur_pos = self.mean_finder()

        if self.fingers.count(1) == 5:
            self.workspace_change()

        elif self.fingers.count(1) == 4:
            self.windows_change()

        elif self.fingers.count(1) == 3:
            self.tabs_change()

        elif self.fingers.count(1) == 2:
            self.audio_controller()

        elif self.fingers.count(1) == 1:
            self.brightness_change()

        elif self.fingers.count(1) == 0:
            GestureRecognitions.change = True

    def count_open_fingers(self):

        one_hand_coord = self.return_point_coord()

        fingers_tip = [4, 8, 12, 16, 20]
        fingers_pos = []

        for tip in fingers_tip:

            if tip != 4:
                if one_hand_coord[tip][2] * self.height < one_hand_coord[tip - 2][2] * self.height:
                    fingers_pos.append(1)
                else:
                    fingers_pos.append(0)
            else:
                if one_hand_coord[tip][2] * self.height < one_hand_coord[tip - 1][2] * self.height:
                    fingers_pos.append(1)
                else:
                    fingers_pos.append(0)

        return fingers_pos

    def mean_finder(self):
        pos = np.array(
            np.mean([[lm.x * self.width, lm.y * self.height] for lm in self.hand.landmark], axis=0).astype(int))
        return pos

    def update_hand_pos(self):
        self.prev_pos = self.mean_finder()
        GestureRecognitions.change = False

    def return_point_coord(self):
        lm_List = []

        for id, lm_cord in enumerate(self.hand.landmark):
            x_pix = lm_cord.x * self.width
            y_pix = lm_cord.y * self.height
            lm_List.append((id, x_pix, y_pix))
        return lm_List

    def workspace_change(self):
        side = self.calculate_change()
        if side != "null":
            if side == "up":
                autoscr.ScreenController.change_workspace("New")
            elif side == "down":
                autoscr.ScreenController.change_workspace("Close")
            elif side == "right":
                autoscr.ScreenController.change_workspace("Right")
            elif side == "left":
                autoscr.ScreenController.change_workspace("Left")

    def windows_change(self):
        side = self.calculate_change()
        if side != "null":
            if side == "up":
                autoscr.ScreenController.change_windows(self, "Close")
            elif side == "down":
                autoscr.ScreenController.change_windows(self, "Minimize")
            elif side == "right":
                autoscr.ScreenController.change_windows(self, "Right")
            elif side == "left":
                autoscr.ScreenController.change_windows(self, "Left")

    def tabs_change(self):
        side = self.calculate_change()
        # if side != "null":
        #     if side == "up":
        #         autoscr.ScreenController.change_tab("New")
        #     elif side == "down":
        #         autoscr.ScreenController.change_tab("Close")
        #     elif side == "right":
        #         autoscr.ScreenController.change_tab("Right")
        #     elif side == "left":
        #         autoscr.ScreenController.change_tab("Left")

    def audio_controller(self):
        pass

    def brightness_change(self):
        pass

    def calculate_change(self, threshold=300):
        if abs(self.cur_pos[0] - self.prev_pos[0]) > threshold:
            GestureRecognitions.change = True

            if self.cur_pos[0] - self.prev_pos[0] > 0:
                return "right"

            else:
                return "left"

        elif abs(self.cur_pos[1] - self.prev_pos[1]) > 200:
            GestureRecognitions.change = True

            if self.cur_pos[1] - self.prev_pos[1] > 0:
                return "down"

            else:
                return "up"

        return "null"

    def check_further_change(self):

        while True:
            self.hand_detection_from_image()
            if self.multi_hands:
                self.hand = self.multi_hands[0]
            if self.hand:
                self.cur_pos = self.mean_finder()
                side = self.calculate_change(threshold=100)
                if side != "null" or self.count_open_fingers().count(1) == 3:
                    if side == "left":
                        pag.hotkey('shift', 'tab')
                    elif side == "right":
                        pag.hotkey('tab')
                    self.prev_pos = self.mean_finder()
                if self.count_open_fingers().count(1) == 2:
                    break
                self.hand = None
        return True

