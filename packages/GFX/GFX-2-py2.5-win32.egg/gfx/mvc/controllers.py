import pygame



class Controller(object):
    pass


class GUIInput(Controller):
    def __init__(self, mediator):
        self.mediator = mediator

    def poll(self):
        signal = self.mediator.signal
        for event in pygame.event.get():
            signal(pygame.event.event_name(event.type), event)


class Loop(Controller):
    def __init__(self, mediator, step_size=50, max_frame_time=500):
        self.step_size = step_size
        self.max_frame_time = max_frame_time
        self.mediator = mediator

    def stop(self):
        self.running = False

    def start(self):
        step_size = self.step_size
        max_frame_time = self.max_frame_time
        signal = self.mediator.signal
        fps_clock = pygame.time.Clock()
        get_ticks = pygame.time.get_ticks
        now = get_ticks() + step_size
        self.running = True
        while(self.running):
            T = get_ticks()

            if T-now > max_frame_time:
                now = T - step_size
            
            while(T-now >= step_size):
                signal('Tick', step_size)
                now += step_size
            else:
                pygame.time.wait(0)
            fps_clock.tick()
            signal('Render', ((1.0*T)-now)/step_size)
            signal('HandleEvents')

        print 'FPS:', fps_clock.get_fps()


    

