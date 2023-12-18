# 2D Ball Balancing

[![2D Ball Balancing Demo](http://img.youtube.com/vi/qAyBT8XbTig/0.jpg)](http://www.youtube.com/watch?v=qAyBT8XbTig "2D Ball Balancing Demo")

This project uses a PID controller to balance a ball on a 2D plane. The ball's position is tracked using a camera and the ball's movement is controlled using two servos.

## Project Structure

- `main.py`: The main script that runs the ball tracking program.
- `controller.py`: Contains the `PIDController` and `ServoController` classes for controlling the ball's movement.
- `tracker.py`: Contains the `BallTracker` class for tracking the ball's position using a camera.
- `util.py`: Contains utility functions used throughout the project.
- `requirements.txt`: Lists the Python dependencies required for this project.

## How to Run

1. Install the required Python dependencies:

```sh
sudo apt install python3-pigpio
pip install -r requirements.txt
```

2. Run the main script:

```sh
sudo pigpiod
python main.py
```

## License
MIT
