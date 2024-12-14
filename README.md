# Signal Generator Communicator

Signal Generator Communicator is a Python-based GUI application for controlling a signal generator, allowing users to send power level commands (in dBm) via a user-friendly interface. It supports configuration of the signal generator's IP address and includes validation for power level ranges.

## Features

- Set power levels in dBm with precise formatting.
- Toggle between positive and negative values.
- Configure the IP address of the signal generator.
- Validate input to ensure power levels remain within a safe range (-12 dBm to 12 dBm).
- Simple and intuitive interface with a numeric keypad.
- Save and load signal generator IP configuration to/from a file.

---

## Prerequisites

- **Python Version**: Python 3.7 or higher.
- **Required Libraries**:
    - `tkinter` (Standard Library)
    - `pyvisa` (`pip install pyvisa`)
    - `pyvisa-py` (`pip install pyvisa-py`)
    - `os` and `sys` (Standard Library)

---