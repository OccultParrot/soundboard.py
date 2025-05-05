import argparse
import time as t
import tkinter as tk
import threading

import sounddevice as sd
import numpy

assert numpy  # avoid "imported but unused" message (W0611)

class SoundBoardPipeline:
    def __init__(self, device: tuple[int, int], channels: int):
        self.device: tuple[int, int] = device
        self.channels: int = channels
        self.active: bool = False
        self.stream = None

    def callback(self, indata, outdata, frames, time, status):
        if status:
            print(status)
        outdata[:] = indata

    def start(self, caller=None):  # Added caller parameter
        if self.active:  # Prevent starting multiple times
            print("Pipeline already active")
            return

        self.active = True
        print("Pipeline started")
        try:
            with sd.Stream(device=self.device, samplerate=44100, channels=self.channels,
                           callback=self.callback) as stream:
                self.stream = stream
                while self.active:
                    t.sleep(0.01)

                print("Pipeline stopped")
                self.stream = None

        except Exception as e:
            print(f"Error in pipeline: {e}")
            self.active = False
            self.stream = None

    def stop(self):
        print("Stopping pipeline")
        self.active = False


class SoundBoard:
    def __init__(self):
        # The actual sound part of the soundboard. This class is all GUI stuff
        self.pipeline = SoundBoardPipeline(device=sd.default.device, channels=1)

        # Setting up the GUI
        self.root = tk.Tk()
        self.root.title("SoundBoard")
        self.root.geometry("800x600")

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        self.on_off_button = tk.Button(self.frame, text="▶", font=("Arial", 20))
        self.on_off_button.pack(side="left")
        self.on_off_button.bind("<Button-1>", lambda e: threading.Thread(target=self.pipeline_on_off).start())

    def pipeline_on_off(self):
        # Toggle the pipeline state
        if self.pipeline.active:
            # If pipeline is active, stop it
            self.pipeline.stop()
            self.on_off_button.config(text="▶")
        else:
            # If pipeline is not active, start it
            threading.Thread(target=lambda: self.pipeline.start(self)).start()
            self.on_off_button.config(text="⏸")

    def run(self):
        """ Sets up the audio pipeline, and runs the GUI """
        # Running the GUI
        self.root.mainloop()


if __name__ == "__main__":
    sb = SoundBoard()

    print("Running Sound Board GUI")
    sb.run()