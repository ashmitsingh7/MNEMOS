# MNEMOS Troubleshooting Guide

## Common Issues

### 1. ROS 2 Not Found or Commands Not Working

**Symptoms**: `ros2 command not found`, `could not find a version`, errors when running `ros2` commands.

**Resolution**:
- Ensure ROS 2 Jazzy is installed: `sudo apt install ros2-jazzy-desktop`
- Source the setup file: `source /opt/ros/jazzy/setup.bash`
- Add to bashrc permanently: `echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrch && source ~/.bashrc`
- Verify: `ros2 --version`

### 2. Gazebo Harmless or Fails to Launch

**Symptoms**: `gz: command not found`, Gazebo crashes on startup, black screen in RViz2.

**Resolution**:
- Install Gazebo Harmonic: `sudo apt install gz-harmonic`
- Verify version: `gz sim -v` should output `Gazebo Sim 8`
- Check display: Ensure X11/Wayland display is available
- Try running with `--verbose` flag for error details

### 3. RTAB-Map Launch Failures

**Symptoms**: `process died`, `module not found`, `library not found` errors with RTAB-Map.

**Resolution**:
- Install RTAB-Map packages: `sudo apt install ros2-jazzy-rtabmap-ros ros2-jazzy-rtabmap`
- Verify libpng and other dependencies
- Check RTAB-Map database path permissions
- Launch with: `ros2 launch rtabmap_ocs/rtabmap.launch.py`

### 4. Navigation Stack Issues

**Symptoms**: `nav2 not found`, planning server fails, battery recovery behaviors not working.

**Resolution**:
- Install navigation packages: `sudo apt install ros2-jazzy-nav2-bringup ros2-jazzy-nav2`
- Ensure all Nav2 plugins are built: `colcon build --packages-select nav2_*`
- Check BT (Behavior Tree) configuration files
- Verify plugin.xml entries are correct

### 5. Python Package Import Errors

**Symptoms**: `ModuleNotFoundError: No module named 'cv2'`, `No module named 'rtabmap'`, `numpy version mismatch`.

**Resolution**:
- Upgrade pip: `pip3 install --upgrade pip`
- Reinstall packages: `pip3 install --force-reinstall numpy opencv-python`
- Check Python version compatibility: `python3 --version` should be 3.12
- For PyTorch: Ensure compatible version for Python 3.12

### 6. TF Tree Errors

**Symptoms**: `transform timed out`, `child frame not found`, `lookup would result in extrapolation error`.

**Resolution**:
- Check coordinate frame names: Verify `world`, `base_link`, `camera_link` exist
- Ensure TF publishers are running
- Check for publish_rate mismatches
- Use `ros2 run tf2_ros tf2echo /world /base_link` to debug
- Verify `<frame_id>` values in your launch files

### 7. Simulation Performance Issues

**Symptoms**: Low FPS in Gazebo, slow processing, laggy RViz2.

**Resolution**:
- Reduce Gazebo physics step size
- Lower RViz2 display update rates
- Simplify RViz2 visualizations
- Check for circular TF dependencies
- Reduce point cloud density in perception pipeline

### 8. Database Corruption (SQLite)

**Symptoms**: Episode data lost, unable to read memory files, `database is locked` errors.

**Resolution**:
- Use `sqlite3` command with `-readonly` flag
- Ensure single writer at a time (use WAL mode)
- Check for concurrent access issues
- Increase SQLite journal size if needed

### 9. Web Interface Not Accessible

**Symptoms**: `Cannot connect to localhost:8080`, `Connection refused`, web page white screen.

**Resolution**:
- Check the web server port configuration
- Ensure the Flask/FastAPI server is running
- Verify no port conflicts (8080, 5000, etc.)
- Check firewall settings
- Look at server stdout/stderr for error messages

### 10. colcon Build Failures

**Symptoms**: `CMake error`, `undefined reference to`, ` missing dependency`.

**Resolution**:
- Ensure all dependencies are installed before building
- Try: `colcon build --packages-select <package> --event-handlers console_direct+:meta`
- Clean and rebuild: `colcon build --packages-select <package> --clean-first`
- Check CMakeLists.txt for correct package format

## Diagnostic Commands

```bash
# Full environment check
echo "=== ROS 2 Version ==="
ros2 --version

echo "=== Python Version ==="
python3 --version

echo "=== OpenCV Version ==="
python3 -c "import cv2; print(cv2.__version__)"

echo "=== NumPy Version ==="
python3 -c "import numpy; print(numpy.__version__)"

echo "=== Gazebo Version ==="
gz sim -v 2>/dev/null || echo "Gazebo not accessible"

echo "=== Installed ROS 2 Packages ==="
ros2 pkg list 2>/dev/null | head -20

echo "=== TF Tree ==="
ros2 run tf2_ros tf2echo /world /base_link 2>/dev/null || echo "TF tree check failed"
```

## When to Ask for Help

- If you've tried all diagnostic commands and the issue persists
- If you encounter error messages not covered in this guide
- If you're unsure whether an issue is related to the MNEMOS platform vs. the underlying ROS 2/Gazebo installation
- Always include the output of the diagnostic commands when reporting issues