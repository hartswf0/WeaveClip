# WeaveClip

A groundbreaking node-based video editing software that reimagines video editing through an intuitive canvas interface and modular workflows.

## Features

- **Canvas-Based Interface**: Zoomable, draggable workspace for intuitive video editing
- **Node-Based Workflow**: Modular video clips with customizable effects and transitions
- **Error Recovery**: Built-in version tracking and undo functionality
- **Interactive Timeline**: Synchronized timeline and node view
- **Dynamic Playback**: Real-time preview with effect visualization
- **Smart Organization**: Group, color-code, and filter nodes

## Requirements

- Python 3.9+
- PyQt6
- OpenCV
- FFmpeg-python

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/weaveclip.git
cd weaveclip
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Development

The project structure follows a modular architecture:
- `src/`: Source code directory
  - `core/`: Core functionality and data models
  - `ui/`: User interface components
  - `utils/`: Utility functions and helpers
  - `effects/`: Video effect processors
- `resources/`: Application resources
- `tests/`: Unit and integration tests

## License

MIT License - See LICENSE file for details
