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
    bot.laser(5)
    bot.retina(True)
    bot.show_image()
    while True:
        pass
