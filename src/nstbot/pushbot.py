import retinabot

class PushBot(retinabot.RetinaBot):
    def initialize(self):
        super(PushBot, self).initialize()
        self.laser(0)
    def disconnect(self):
        self.laser(0)
        super(PushBot, self).disconnect()

    def laser(self, freq, msg_period=None):
        if freq <= 0:
            cmd = '!PA=0\n!PA0=0\n'
        else:
            cmd = '!PA=%d\n!PA0=%d\n' % (int(1000000/freq),
                                         int(500000/freq))
        self.send('laser', cmd, msg_period=msg_period)

if __name__ == '__main__':
    import connection
    bot = PushBot()
    bot.connect(connection.Serial('/dev/ttyUSB0', baud=4000000))
    #bot.connect(connection.Socket('10.162.177.135'))
    bot.laser(150)
    bot.track_frequencies(freqs=[50, 100, 150])
    bot.retina(True)
    bot.show_image()
    bot.track_spike_rate(all=(0,0,128,128))
    import time
    while True:
        time.sleep(1)
