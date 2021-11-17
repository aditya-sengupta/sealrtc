# authored by Aditya Sengupta

import numpy as np
from functools import partial
from .observe_laws import identity, make_kf_observer
from .control_laws import nothing, integrate, lqg_controller

def controller(observe_law, control_law, measurement):
    state = observe_law(measurement[:2]) # TODO generalize
    return control_law(state)

def make_openloop():
    return "ol", partial(
        controller, 
        observe_law=identity, 
        control_law=nothing
    )

def make_integrator(gain=0.1, leak=1.0):
    return f"int_gain_{gain}_leak_{leak}", partial(
        controller, 
        observe_law=identity, 
        control_law=partial(integrate, gain=gain, leak=leak)
    )

def make_kalman_lqg(klqg):
    return f"klqg_nstate_{klqg.state_size}", partial(
        controller, 
        observe_law=partial(kfilter, klqg=klqg), 
        control_law=partial(lqg_controller, klqg=klqg)
    )
