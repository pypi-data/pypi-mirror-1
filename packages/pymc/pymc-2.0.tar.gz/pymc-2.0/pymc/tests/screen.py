import time
import select
import termios
import sys

class Screen:
     def __init__(self):
          self.__attsorig = termios.tcgetattr(sys.stdin.fileno())
          self.__atts = termios.tcgetattr(sys.stdin.fileno())
          #don't echo characters
          self.__atts[3] = self.__atts[3] & ~termios.ECHO
          #non-buffered input (don't wait for <ENTER>) 
          self.__atts[3] = self.__atts[3] & ~termios.ICANON
          termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.__atts)


     def reset(self):
          termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.__attsorig)

     def unfold_message(self, msg, delay):
          try:
               delay=float(delay)
          except ValueError:
               delay=0.100
          for char in msg:
               # Check if the user has hit a key
               if select.select([sys.stdin],[],[],0) == ([sys.stdin],[],[]):
                    delay = 0
                    # Get keystrokes from stdin
                    whocares = os.read(sys.stdin.fileno(), 1024)
               time.sleep(delay)
               sys.stdout.write(char)
               sys.stdout.flush()
          print

if __name__ == "__main__":
     screen = Screen()
     screen.unfold_message("hello, this is a test", 0.1)
     screen.reset()
