
class Loop(object):
    def __init__(self, time_function, wait_function, step_size, max_frame_time, tick_function=lambda time_step:None, render_function=lambda percent:None, event_function=lambda:None):
        """
        time_function: a callable which returns time values
        wait_function: a callable which idles (sleeps the CPU)
        tick_function: a callable which is passed the step size
        render_function: a callable which is passed percentage between steps.
        event_function: a callable which handles events off the pygame event queue
        step_size: number of milliseconds between each simulation step
        max_frame_time: if duration between frames is greater than this value, skip frames.

        The render_function, event_function and tick_function attributes can all be 
        overidden after the loop has started.
        """
        self.time_function = time_function
        self.wait_function = wait_function
        self.tick_function = tick_function
        self.render_function = render_function
        self.event_function = event_function
        self.step_size = step_size
        self.max_frame_time = max_frame_time

    def stop(self):
        self.running = False

    def start(self):
        step_size = self.step_size
        max_frame_time = self.max_frame_time
        get_ticks = self.time_function
        sleep = self.wait_function
        now = get_ticks() + step_size
        self.running = True
        while(self.running):
            T = float(get_ticks())

            if T-now > max_frame_time:
                now = T - step_size
            
            while(T-now >= step_size):
                self.tick_function(step_size)
                now += step_size
            else:
                sleep(0)
            self.render_function((T-now)/step_size)

            self.event_function()

