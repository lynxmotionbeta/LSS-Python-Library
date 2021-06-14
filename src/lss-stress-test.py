from lss import LssPacket, LssBus
import math
import time


# makes a really pretty progress bar string
def make_progress_bar(progress: float, width: int):
    # 0 <= progress <= 1
    progress = min(1, max(0, progress))
    whole_width = math.floor(progress * width)
    remainder_width = (progress * width) % 1
    part_width = math.floor(remainder_width * 8)
    part_char = [" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉"][part_width]
    if (width - whole_width - 1) < 0:
        part_char = ""
    line = "█" * whole_width + part_char + " " * (width - whole_width - 1) + "▍"
    return line


if __name__ == '__main__':
    #baud = 250000
    #baud = 500000
    baud = 921600
    bus = LssBus('/dev/ttyUSB0', baud, low_latency=True)  # open serial port

    #bus.write('#0Q3')  # write a string
    #p = bus.read()
    #print('isr: ', p.decode('utf-8'))

    #bus.write('#0RESET')  # write a string
    #time.sleep(2.0)

    count = 1000000
    n = 0
    errors = 0
    start_time = time.time()
    while n < count:
        #bus.write('#0QN')  # write a string
        #p = bus.read()

        try:
            bus.write('#0QD')  # write a string
            D = bus.read()
            if D.command != 'D':
                raise RuntimeError('expected D reply')

            bus.write('#0QC')  # write a string
            C = bus.read()
            if C.command != 'C':
                raise RuntimeError('expected C reply')

            bus.write('#0QS')  # write a string
            S = bus.read()
            if S.command != 'S':
                raise RuntimeError('expected S reply')
        except Exception as e:
            errors = errors + 1

        n = n + 1
        if n % 2 == 0:
            percent = n / count
            progress_str = make_progress_bar(percent, 25)
            elapsed = time.time() - start_time
            avg_loop_freq = n / elapsed
            print("  Packets {:6} {}  {:3}%  {}E  {:3}Hz".format(
                n, progress_str, round(percent*100), errors, round(avg_loop_freq)
            ), end='\r')

    #bus.write('#0Q3')  # write a string
    #p = bus.read()
    #print('isr: ', p.decode('utf-8'))

    bus.close()

