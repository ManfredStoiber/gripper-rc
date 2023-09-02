# Gripper Remote Control
Small tool for remote controlling the [CARES Gripper](https://github.com/UoA-CARES/Gripper-Code) by hand
![Gripper RC](readme_media/gripper-rc.png)

## Control
- Use quality slider to reduce stream quality for better performance.
- Gripper can be controlled using the sliders or by pressing the specified keys.
- Press "H" to return to home position.

## Installation
You can either use the pre-built container from Docker Hub or build it yourself
### Container from Docker Hub
1. Run docker container: `docker run -it --rm --device=/dev/ttyUSB0 --device=/dev/video0 --device=/dev/video1 -p 5000:5000 manfredstoiber/gripper-rc`
2. Open browser: http://\<host-ip>:5000/

### Build
1. `git clone https://github.com/ManfredStoiber/gripper-rc`
2. `cd gripper-rc`
3. `docker build -t cares/gripper-rc .`
4. Run docker container: `docker run -it --rm --device=/dev/ttyUSB0 --device=/dev/video0 --device=/dev/video1 -p 5000:5000 cares/gripper-rc`
5. Open browser: http://\<host-ip>:5000/

## Known problems:
- Currently only configured for 4-DoF-Gripper
- Gripper sometimes crashes. Although the application tries to restart it, this does not always work. If this occurs, please restart the application
