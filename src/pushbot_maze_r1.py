import socket
import time
import numpy as np
import struct
import atexit
import thread


display_mode = 'quick'
rolling_average_time_window = 10 #number of samples in the rolling average window
window_index = 0 #index into the window
max0 = -65536
min0 = 65536
max1 = -65536
min1 = 65536
max2 = -65536
min2 = 65536
window0 = [None] * rolling_average_time_window
window1 = [None] * rolling_average_time_window
window2 = [None] * rolling_average_time_window
decay = 0.00000001
#decay = 0


class PushBot3(object):
    sensors = dict(compass=512, accel=256, gyro=128, bat= 1)

    running_bots = {}

    @classmethod
    def get_bot(cls, address, port=56000, message_delay=0.01, packet_size=5):
        key = (address, port)
        if key not in PushBot3.running_bots:
            PushBot3.running_bots[key] = PushBot3(address, port,
                                                  message_delay=message_delay,
                                                  packet_size=packet_size)
        return PushBot3.running_bots[key]


    def __init__(self, address, port=56000, message_delay=0.01, packet_size=5):
        self.image = None
        self.regions = None
        self.track_periods = None
        self.spinnaker_address = None
        self.packet_size = packet_size
        assert 4 <= packet_size <=6

        self.laser_freq = None
        self.led_freq = None

        if ',' in address:
            print 'configuring for SpiNNaker', address
            self.spinnaker_address = address.split(',')
            self.socket = None
            return
        print 'connecting...', address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((address, port))
        self.socket.settimeout(0)
        self.key = (address, port)
        self.message_delay = message_delay
        self.last_time = {}

        self.motor(0, 0, force=True)
        self.socket.send('\n\nR\n\n')  # reset the board
        time.sleep(2)
        self.socket.send('!E%d\nE+\n' % (self.packet_size-2))  # turn on retina
        self.socket.send('!M+\n')      # activate motors
        atexit.register(self.stop)
        print '...connected'

        self.ticks = 0
        self.vertex = None

        self.sensor = dict(compass=[0,0,0], accel=[0,0,0],
                           gyro=[0,0,0], bat=[5000], touch=0)
        self.compass_range = None

        thread.start_new_thread(self.sensor_loop, ())

    def count_spikes(self, **regions):
        self.regions = regions
        self.count_regions = {}
        for k,v in regions.items():
            self.count_regions[k] = [0, 0]
    def track_freqs(self, freqs, sigma_t=100, sigma_p=30, eta=0.3,
                                 certainty_scale=10000):
        freqs = np.array(freqs, dtype=float)
        self.track_periods = 500000/freqs
        self.track_certainty_scale = certainty_scale

        self.track_sigma_t = sigma_t
        self.track_sigma_p = sigma_p
        self.track_eta = eta

        self.last_on = np.zeros((128, 128), dtype=np.uint32)
        self.last_off = np.zeros((128, 128), dtype=np.uint32)
        self.p_x = np.zeros_like(self.track_periods) + 64.0
        self.p_y = np.zeros_like(self.track_periods) + 64.0
        self.track_certainty = np.zeros_like(self.track_periods)
        self.good_events = np.zeros_like(self.track_periods, dtype=int)



    def get_spike_rate(self, region):
        return self.count_regions[region][0]


    def show_image(self, decay = 0.5):
        if self.socket is None:
            # TODO: log a warning here
            return
        if self.image is None:
            self.image = np.zeros((128, 128), dtype=float)
            thread.start_new_thread(self.image_loop, (decay,))


    def image_loop(self, decay):
        import pylab
        fig = pylab.figure()
        pylab.ion()
        img = pylab.imshow(self.image, vmax=1, vmin=-1,
                                       interpolation='none', cmap='binary')

        if self.track_periods is not None:
            colors = ([(0,0,1), (0,1,0), (1,0,0), (1,1,0), (1,0,1)] * 10)[:len(self.p_y)]
            scatter = pylab.scatter(self.p_y, self.p_x, s=50, c=colors)
        else:
            scatter = None

        while True:
            #fig.clear()
            #print self.track_periods
            #pylab.plot(self.delta)
            #pylab.hist(self.delta, 50, range=(0000, 15000))
            img.set_data(self.image)
            if scatter is not None:
                scatter.set_offsets(np.array([self.p_y, self.p_x]).T)
                c = [(r,g,b,min(self.track_certainty[i],1)) for i,(r,g,b) in enumerate(colors)]
                scatter.set_color(c)
            if display_mode == 'quick':
                # this is much faster, but doesn't work on all systems
                fig.canvas.draw()
                fig.canvas.flush_events()
            else:
                # this works on all systems, but is kinda slow
                pylab.pause(0.001)
            self.image *= decay

    def get_compass(self):
        return self.sensor['compass']
    def get_accel(self):
        return self.sensor['accel']

    def get_gyro(self):
        return self.sensor['gyro']

    def get_bat(self):
        return self.sensor['bat']

    def get_touch(self):
        return self.sensor['touch']

    def set_touch(self, x):
        self.sensor['touch'] = x

    def set_accel(self, data):
        x, y, z = data
        self.sensor['accel'] = float(x)/10000, float(y)/10000, float(z)/10000

    def set_bat(self, data):
        x = data
        self.sensor['bat'] = float(x)
        #print(x)

    def set_gyro(self, data):
        x, y, z = data
        self.sensor['gyro'] = float(x)/5000, float(y)/5000, float(z)/5000

    def set_compass(self, data):

        global min0, max0, min1, max1, min2, max2
        global window_index, rolling_average_time_window
        global window0, window1, window2
        global decay

        if data[0] == 0 and data[1] == 0 and data[2] == 0:
            # throw out invalid data
            return


        if window_index == 0:
            min0 = data[0]
            min1 = data[1]
            min2 = data[2]
            max0 = data[0]
            max1 = data[1]
            max2 = data[2]
            averages = [0, 0, 0]
            self.sensor['compass'] = averages

#        if data[0] < min0 - abs(0.1*min0):
#            data[0] = min0 - abs(0.1*min0)
#        if data[0] > max0 + abs(0.1*max0):
#            data[0] = max0 + abs(0.1*max0)
        min0 = min(min0, data[0])
        max0 = max(max0, data[0])

#        if data[1] < min1 - abs(0.1*min1):
#            data[1] = min1 - abs(0.1*min1)
#        if data[1] > max1 + abs(0.1*max1):
#            data[1] = max1 + abs(0.1*max1)
        min1 = min(min1, data[1])
        max1 = max(max1, data[1])

#        if data[2] < min2 - abs(0.1*min2):
#            data[2] = min2 - abs(0.1*min2)
#        if data[2] > max2 + abs(0.1*max2):
#            data[2] = max2 + abs(0.1*max2)
        min2 = min(min2, data[2])
        max2 = max(max2, data[2])


        #decay minimum and maximum

        window0[window_index % rolling_average_time_window] = data[0]
        window1[window_index % rolling_average_time_window] = data[1]
        window2[window_index % rolling_average_time_window] = data[2]

        fract = min(window_index+1, rolling_average_time_window)
        if window_index != 0:
            averages = [float(sum(filter(None, window0)))/float(fract), float(sum(filter(None, window1)))/float(fract), float(sum(filter(None, window2)))/float(fract)]
            self.sensor['compass'] = [float(2*((averages[0]-min0)))/float(max0-min0)-1, float(2*((averages[1]-min1))/float(max1-min1))-1, float(2*((averages[2]-min2))/float(max2-min2))-1]

        min0 = min0 + decay*(max0 - min0)
        max0 = max0 - decay*(max0 - min0)
        min1 = min1 + decay*(max1 - min1)
        max1 = max1 - decay*(max1 - min1)
        min2 = min2 + decay*(max2 - min2)
        max2 = max2 - decay*(max2 - min2)
        window_index = window_index + 1
#        print "0: ",min0, max0, data[0], averages[0], self.sensor['compass'][0]
#        print "1: ",min1, max1, data[1], averages[1], self.sensor['compass'][1]
#        print "2: ",min2, max2, data[2], averages[2], self.sensor['compass'][2]
#        print self.sensor['compass']

#        diff = self.compass_range[0] - self.compass_range[1]
#        value = [0, 0, 0]
#        for i in range(3):
#            if diff[i] > 0:
#                value[i] = ((data[i]-self.compass_range[1][i])/diff[i] - 0.5) *2


    def process_ascii(self, msg):
        index = msg.find('-')
        if index > -1:
            msg = msg[index:]
            try:
                if msg.startswith('-S9 '):
                    x,y,z = msg[4:].split(' ')
                    self.set_compass((int(x), int(y), int(z)))
                elif msg.startswith('-S8 '):
                    x,y,z = msg[4:].split(' ')
                    self.set_accel((int(x), int(y), int(z)))
                elif msg.startswith('-S0 '):
                    x = msg[4:]
                    self.set_bat(int(x))
                elif msg.startswith('-S7 '):
                    x,y,z = msg[4:].split(' ')
                    self.set_gyro((int(x), int(y), int(z)))
                elif msg.startswith('-S100 '):
                    x = msg[6:]
                    self.set_touch(int(x))
                else:
                    pass
                    #print 'unknown msg', msg
            except:
                pass
                #print 'invalid msg', msg

    def sensor_loop(self):
        old_data = None
        packet_size = self.packet_size
        buffered_ascii = ''
        while True:
            try:
                data = self.socket.recv(1024)
                if old_data is not None:
                    data = old_data + data
                    old_data = None

                data_all = np.fromstring(data, np.uint8)
                ascii_index = np.where(data_all[::packet_size] < 0x80)[0]

                offset = 0
                while len(ascii_index) > 0:
                    index = ascii_index[0]*packet_size
                    stop_index = np.where(data_all[index:] >=0x80)[0]
                    if len(stop_index) > 0:
                        stop_index = index + stop_index[0]
                    else:
                        stop_index = len(data)

                    #print `data[offset+index:offset+stop_index]`
                    buffered_ascii += data[offset+index:offset+stop_index]
                    data_all = np.hstack((data_all[:index],
                                          data_all[stop_index:]))
                    offset += stop_index - index
                    ascii_index = np.where(data_all[::packet_size] < 0x80)[0]

                extra = len(data_all) % packet_size
                if extra != 0:
                    old_data = data[-extra:]
                    data_all = data_all[:-extra]
                if len(data_all) > 0:
                    self.process_retina(data_all)

                while '\n' in buffered_ascii:
                    cmd, buffered_ascii = buffered_ascii.split('\n', 1)
                    self.process_ascii(cmd)

            except socket.error as e:
                pass

    delta = None
    last_t = None
    last_rt = 0
    counter = 0
    last_timestamp = None
    def process_retina(self, data):
        packet_size = self.packet_size
        x = data[::packet_size] & 0x7f    # actually y  TODO: swap this
        y = data[1::packet_size] & 0x7f   # actually x
        if self.image is not None:
            value = np.where(data[1::packet_size]>=0x80, 1, -1)
            self.image[x, y] += value
        if self.regions is not None:
            tau = 0.05 * 1000000
            for k, region in self.regions.items():
                minx, miny, maxx, maxy = region
                # TODO: fix this swapped x,y stuff
                index = (minx <= y) & (y<maxx) & (miny <= x) & (x<maxy)
                count = np.sum(index)
                t = (int(data[-2]) << 8) + data[-1]

                old_count, old_time = self.count_regions[k]

                dt = float(t - old_time)
                if dt < 0:
                    dt += 65536
                count /= dt / 1000.0

                decay = np.exp(-dt/tau)
                new_count = old_count * (decay) + count * (1-decay)

                self.count_regions[k] = new_count, t
            if self.counter % 10 == 0:
                print {k:v[0] for k,v in self.count_regions.items()}
            self.counter += 1

        if self.track_periods is not None:
            t = data[2::packet_size].astype(np.uint32)
            t = (t << 8) + data[3::packet_size]
            if packet_size >= 5:
                t = (t << 8) + data[4::packet_size]
            if packet_size >=6:
                t = (t << 8) + data[5::packet_size]

            if self.last_timestamp is not None:
                dt = float(t[-1]) - self.last_timestamp
                if dt < 0:
                    dt += 1 << (8 * (packet_size-2))
            else:
                dt = 1
            self.last_timestamp = t[-1]


            #now = time.clock()
            #if self.last_t is None or now > self.last_t + 0.1:
            #    self.last_t = now
            #    print 'dt', (t[-1] - self.last_rt)
            #    self.last_rt = t[-1]
                #print 't %08x' % t[-1]
                #if len(t) > 2:
                #    print 't %08x %08x %08x' % (t[-3], t[-2], t[-1])




            #print t
            index_on = (data[1::packet_size] & 0x80) > 0
            index_off = (data[1::packet_size] & 0x80) == 0

            #delta = np.where(index_on,
            #                 t - self.last_off[x, y],
            #                 t - self.last_on[x, y])
            delta = np.where(index_on, t - self.last_on[x, y], 0)

            #delta = t
            #if self.delta is None:
            #    self.delta = delta
            #else:
            #    self.delta = np.hstack((self.delta, delta))

            #if len(self.delta) > 1000:
            #    self.delta = self.delta[-1000:]



            self.last_on[x[index_on],
                         y[index_on]] = t[index_on]
            #self.last_off[x[index_off],
            #              y[index_off]] = t[index_off]

            tau = 0.05 * 1000000
            decay = np.exp(-dt/tau)
            self.track_certainty *= decay

            for i, period in enumerate(self.track_periods):
                eta = self.track_eta
                t_exp = period * 2
                sigma_t = self.track_sigma_t    # in microseconds
                sigma_p = self.track_sigma_p    # in pixels
                t_diff = delta.astype(np.float) - t_exp

                w_t = np.exp(-(t_diff**2)/(2*sigma_t**2))
                #w = np.sum(w_t)
                #eta *= w
                #print w
                #print t_diff[:5]
                #print w_t[:5]
                px = self.p_x[i]
                py = self.p_y[i]

                dist2 = (x - px)**2 + (y - py)**2
                w_p = np.exp(-dist2/(2*sigma_p**2))

                ww = w_t * w_p
                c = sum(ww) * self.track_certainty_scale / dt

                self.track_certainty[i] += (1-decay) * c

                # horrible heuristic for figuring out if we have good
                # data by chekcing the proportion of events that are
                # within sigma_t of desired period
                #self.good_events[i] += (w_t>0.5).sum()


                for j, w in enumerate(eta * ww):
                    if w > 0.02:
                        px += w * (x[j] - px)
                        py += w * (y[j] - py)
                self.p_x[i] = px
                self.p_y[i] = py

                '''
                # faster, but less accurate method:
                # update position estimate
                try:
                    r_x = np.average(x, weights=w_t*w_p)
                    r_y = np.average(y, weights=w_t*w_p)
                    self.p_x[i] = (1-eta)*self.p_x[i] + (eta)*r_x
                    self.p_y[i] = (1-eta)*self.p_y[i] + (eta)*r_y
                except ZeroDivisionError:
                    # occurs in np.average if weights sum to zero
                    pass
                '''

            #print self.p_x, self.p_y, self.track_certainty

    def send(self, key, cmd, force):
        if self.socket is None:
            return
        now = time.time()
        if force or self.last_time.get(key, None) is None or (now >
                self.last_time[key] + self.message_delay):
            self.socket.send(cmd)
            self.last_time[key] = now

    def activate_sensor(self, name, freq):
        if self.socket is None:       # spinnaker
            return
        bitmask = PushBot3.sensors[name]
        period = int(1000.0/freq)
        try:
            self.socket.send('!S+%d,%d\n' % (bitmask, period))
        except:
            self.disconnect()

    def disconnect(self):
        del PushBot3.running_bots[self.key]
        self.socket.close()


    def motor(self, left, right, force=False):
            left = int(left*100)
            right = int(right*100)
            if left > 100: left=100
            if left < -100: left=-100
            if right > 100: right=100
            if right < -100: right=-100
            cmd = '!MVD0=%d\n!MVD1=%d\n' % (left, right)
            self.send('motor', cmd, force)

    def omni_motor(self, x, y, r, force=False):
        a = 0*x    -  1.0*y  + 1.0*r
        b = 0.8*x  +  0.45*y  + 1.0*r
        c = 0.8*x  -  0.45*y  - 1.0*r
        a = int(a * 100)
        b = int(b * 100)
        c = int(c * 100)
        a = min(max(a, -100), 100)
        b = min(max(b, -100), 100)
        c = min(max(c, -100), 100)
        cmd = '!MVD0=%d\n!MVD1=%d\n!MVD2=%d' % (a, b, c)
        self.send('motor', cmd, force)

    def beep(self, freq, force=False):
        if freq <= 0:
            cmd = '!PB=0\n!PB0=0\n'
        else:
            cmd = '!PB=%d\n!PB0=%%50\n' % int(1000000/freq)
        self.send('beep', cmd, force)

    def laser(self, freq, force=False):
        if self.socket is not None:
            if freq <= 0:
                cmd = '!PA=0\n!PA0=0\n'
            else:
                cmd = '!PA=%d\n!PA0=%d\n' % (int(1000000/freq),
                                             int(500000/freq))
            self.send('laser', cmd, force)
        else:
            self.laser_freq = freq

    def led(self, freq, force=False):
        if self.socket is not None:
            if freq <= 0:
                cmd = '!PC=0\n!PC0=0\n!PC1=0'
            else:
                cmd = '!PC=%d\n!PC0=%d\n!PC1=%d\n' % (int(1000000/freq),
                        int(500000/freq), int(500000/freq))
            self.send('led', cmd, force)
        else:
            self.led_freq = freq

    def stop(self):
        if self.socket is not None:
            self.beep(0, force=True)
            #self.laser(0, force=True)
            #self.led(0, force=True)
            self.socket.send('!M-\n')
            self.socket.send('E-\n')
            self.socket.send('!S-\n')


if __name__ == '__main__':
    #bot1 = PushBot3('10.162.177.135')
    #bot1.laser(200)
    #bot1.led(100)
    IP = raw_input("Please enter the robot IP: ")
    print "IP address entered is: ", IP
    bot = PushBot3(IP, packet_size=4)
    #bot = PushBot3('1,0,EAST')
    #bot.activate_sensor('compass', freq=100)
    #bot.activate_sensor('gyro', freq=100)
    #bot.count_spikes(all=(0,0,128,128), left=(0,0,64,128), right=(64,0,128,128))
    #bot.activate_sensor('bat', freq=100)

    bot.laser(200)
    bot.track_freqs([300, 200, 100], sigma_p=40)
    bot.show_image()
    #import time

    while True:
        #bot.omni_motor(0, 1, 0)
        time.sleep(0.1)

