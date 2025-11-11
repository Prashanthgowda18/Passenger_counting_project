# Passenger Movement Detection Improvements

## Issues Addressed

The original system had several accuracy issues when detecting passenger movement to the right side of the bus:

1. **Single line detection**: Only used horizontal line in middle of frame
2. **No direction validation**: Didn't properly validate right-side movement
3. **Poor tracking parameters**: Tracking was too sensitive/insensitive
4. **No movement filtering**: No validation to prevent false positives

## Improvements Made

### 1. Enhanced Configuration (`config.py`)
- Added `RIGHT_SIDE_THRESHOLD = 0.6` - threshold for right side movement (60% from left edge)
- Added `MIN_MOVEMENT_PIXELS = 20` - minimum pixels moved to count as valid movement
- Added `MOVEMENT_HISTORY_FRAMES = 5` - frames to track for movement validation
- Increased `DIRECTION_TOLERANCE` from 5 to 10 pixels for better tolerance

### 2. Improved Tracking (`tracker.py`)
- Enhanced `TrackedObject` class with new properties:
  - `entered`: tracks if object has entered
  - `exited`: tracks if object has exited
  - `moved_right`: tracks if object moved to right side
  - `initial_position`: stores initial position for movement calculation
- Added `check_right_movement()` method to validate right-side movement
- Improved tracking parameters: `maxDisappeared=40`, `maxDistance=60`

### 3. Enhanced Main Detection Logic (`main.py`)
- **Color-coded bounding boxes**:
  - Green: Normal tracking
  - Yellow: Moved to right side
  - Red: Entered the bus
- **Right-side movement detection**: Validates when passengers move to right side
- **Movement validation**: Requires minimum movement pixels to prevent false positives
- **Improved line crossing logic**: Uses movement history for better accuracy
- **Visual indicators**: Added right-side line and counter display

### 4. Key Features Added

#### Right-Side Movement Detection
- Tracks when passengers move beyond 60% of frame width
- Validates significant movement (minimum 20 pixels)
- Prevents false positives from stationary objects

#### Movement Validation
- Requires minimum movement over 5 frames
- Calculates total movement for validation
- Prevents counting stationary or jittery detections

#### Visual Feedback
- Right-side indicator line (magenta)
- Separate counter for right-side passengers
- Color-coded bounding boxes for easy identification

## Usage

The improved system now provides:
1. **More accurate entry/exit detection** with movement validation
2. **Right-side movement tracking** with visual indicators
3. **Reduced false positives** through movement filtering
4. **Better visual feedback** with color-coded tracking
5. **Separate counters** for total passengers and right-side passengers

## Configuration Options

You can adjust these parameters in `config.py`:
- `RIGHT_SIDE_THRESHOLD`: Adjust right-side detection threshold (0.0-1.0)
- `MIN_MOVEMENT_PIXELS`: Minimum movement required for validation
- `MOVEMENT_HISTORY_FRAMES`: Number of frames to track for validation
- `DIRECTION_TOLERANCE`: Pixel tolerance for direction detection

## Expected Results

The system should now be much more accurate at:
- Detecting when passengers enter the bus
- Tracking movement to the right side
- Reducing false positive counts
- Providing clear visual feedback of passenger status


