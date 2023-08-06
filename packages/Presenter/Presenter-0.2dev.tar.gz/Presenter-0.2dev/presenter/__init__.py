#!/usr/bin/env python

__version__ = 0.2

def main():
    from presenter.interface import run_application
    from presenter.control import ControlWindow

    window = ControlWindow()
    run_application(window)

if __name__ == '__main__':
    main()

