import nstbot

bot = nstbot.pushbot.PushBot()
#bot.connect(connection.Serial('/dev/ttyUSB0', baud=4000000))
bot.connect(nstbot.connection.Socket('10.162.177.135'))

bot.laser(150)
bot.track_frequencies([150])
bot.retina(True)

import time
import random
y_prev = None
dy = 0
dt = 0.1


direction = 1
while True:
    x, y, c = bot.get_frequency_info(0)
    if y_prev is not None:
        dy = (y - y_prev) / dt
    y_prev = y

    left = 0
    right = 0

    # fwd
    if y < 100:
        left += 0.08
        right += 0.08

    # back
    if y > 100:
        left -= 0.06
        right -= 0.06


    # avoid
    if y > 90:
        if dy > 5 and random.random() < dy*0.01:
            print 'swap'
            direction = -direction
        left += direction * 0.04
        right -= direction * 0.04

    left *= 2
    right *= 2


    print y, dy 


    bot.motor(left, right)

    time.sleep(dt)
