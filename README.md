# Indoor Navigation System Using Apriltags
This project is an indoor navigation system that utilizes AprilTags for initial pose estimation and combines multiple components to create a reliable navigation experience. The system is intended to help users navigate indoor spaces with real-time updates.

## 1. Pose Estimation Using Apriltags - Completed
- The camera detects AprilTags, and detection information is used to calculate the user's pose (x, y, angle), using **PnP (Perspective-n-Point)**.
- This component sets the initial user position and orientation for pathfinding.

## 2. Draw Map (Server Side) - Completed
A GUI tool for developers to create and modify the floorplan.

**Features:**
- **Add/Remove Walls**: Define navigable and restricted areas.
- **Set Destinations and Waypoints**: Place destinations with orientation, aiding in directional guidance.

This tool generates JSON-based map files, used by the pathfinding component.

## 3. Pathfinder - Completed
- Uses the **A-star** algorithm to find the optimal route from the user's current position to a selected destination.
- Input: User's initial pose and target destination.
- Output: A list of waypoints representing the path and navigation messages to guide the user along the route.

## 4. Android App Development - Pending
Developing an Android app for real-time navigation assistance, integrating camera-based pose estimation and interactive UI for user navigation.

## 5. IMU Integration - Pending
- Purpose: To provide continuous pose updates between AprilTag detections, ensuring smooth navigation.
- Current Status: Not started; additional research required to ensure accuracy and reliable IMU data fusion.

## Future Improvements and Explorations
- **Alternative Localization Methods**: Exploring other localization technologies such as **Ultra-Wideband (UWB), WiFi positioning, SLAM (Simultaneous Localization and Mapping), and VIO (Visual-Inertial Odometry)** as potential alternatives to AprilTags for improved accuracy and reliability.
- **Localization Accuracy**: Continuing research into IMU integration and alternative localization methods to enhance navigation consistency between detections.
- **User Interface Enhancements**: Adding features to visualize real-time orientation and provide user-friendly directions.