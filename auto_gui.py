import pyautogui
import sys
import time

pyautogui.PAUSE = 0.7


def main():
    try:
        time.sleep(5)
        while True:
            pyautogui.moveTo(1265, 196)
            pyautogui.click()
            pyautogui.moveTo(961, 377)
            pyautogui.click()
            pyautogui.moveTo(1057, 394, duration=1.0)
            time.sleep(5)
            pyautogui.moveTo(943, 238)
            pyautogui.click()
            # time.sleep(1)
            pyautogui.moveTo(673, 416)
            pyautogui.click()
            pyautogui.moveTo(729, 555)
            pyautogui.click()
            pyautogui.press('right')

    except KeyboardInterrupt:
        print('\n')


def record_mouse():
    try:
        while True:
            x, y = pyautogui.position()
            positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
            print(positionStr)
            time.sleep(3)
    except KeyboardInterrupt:
        print('\n')


if __name__ == '__main__':
    main()