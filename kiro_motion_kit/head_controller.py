import math
import cv2
import mediapipe as mp
import numpy as np
from dataclasses import dataclass
from typing import Optional


mp_face_mesh = mp.solutions.face_mesh


def rotation_matrix_to_angles(rotation_matrix):
    """Calculate Euler angles from rotation matrix.
    
    :param rotation_matrix: A 3*3 matrix with the following structure
        [Cosz*Cosy  Cosz*Siny*Sinx - Sinz*Cosx  Cosz*Siny*Cosx + Sinz*Sinx]
        [Sinz*Cosy  Sinz*Siny*Sinx + Sinz*Cosx  Sinz*Siny*Cosx - Cosz*Sinx]
        [  -Siny             CosySinx                   Cosy*Cosx         ]
    :return: Angles in degrees for each axis
    """
    x = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
    y = math.atan2(
        -rotation_matrix[2, 0],
        math.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
    )
    z = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
    return np.array([x, y, z]) * 180.0 / math.pi


@dataclass
class HeadTrackingState:
    """Representation of the current head pose state.
    
    Attributes
    ----------
    is_present: Whether a face is currently detected.
    x_axis: Head rotation around x-axis in degrees (nodding up/down).
    y_axis: Head rotation around y-axis in degrees (turning left/right).
    z_axis: Head rotation around z-axis in degrees (tilting left/right).
    """
    is_present: bool = False
    x_axis: Optional[float] = None
    y_axis: Optional[float] = None
    z_axis: Optional[float] = None


class HeadTracker:
    """Head pose tracking using Mediapipe Face Mesh.
    
    This class detects head orientation (pitch, yaw, roll) from camera frames.
    """
    
    # Face landmarks used for pose estimation
    # 1: nose tip, 9: chin, 57/287: mouth corners, 130/359: eye corners
    POSE_LANDMARKS = [1, 9, 57, 130, 287, 359]
    
    # 3D model points for face landmarks in real-world coordinates
    FACE_3D_MODEL = np.array([
        [285, 528, 200],   # Nose tip
        [285, 371, 152],   # Chin
        [197, 574, 128],   # Left mouth corner
        [173, 425, 108],   # Left eye corner
        [360, 574, 128],   # Right mouth corner
        [391, 425, 108],   # Right eye corner
    ], dtype=np.float64)
    
    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        self._face_mesh = mp_face_mesh.FaceMesh(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.state = HeadTrackingState()
    
    def process_frame(self, frame_bgr):
        """Process a BGR frame and update internal head pose state.
        
        Parameters
        ----------
        frame_bgr: np.ndarray
            BGR image from a camera or video.
        
        Returns
        -------
        frame_bgr: np.ndarray
            The same frame, optionally annotated with pose information.
        HeadTrackingState
            The updated head tracking state.
        """
        # Convert BGR to RGB for Mediapipe
        image = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self._face_mesh.process(image)
        
        # Convert back to BGR for display
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Default state when no face is present
        self.state = HeadTrackingState(
            is_present=False,
            x_axis=None,
            y_axis=None,
            z_axis=None,
        )
        
        if results.multi_face_landmarks:
            h, w, _ = image.shape
            face_landmarks = results.multi_face_landmarks[0]
            
            # Extract 2D coordinates of key landmarks
            face_2d = []
            for idx, lm in enumerate(face_landmarks.landmark):
                if idx in self.POSE_LANDMARKS:
                    x, y = int(lm.x * w), int(lm.y * h)
                    face_2d.append([x, y])
            
            face_2d = np.array(face_2d, dtype=np.float64)
            
            # Camera matrix
            focal_length = 1 * w
            cam_matrix = np.array([
                [focal_length, 0, w / 2],
                [0, focal_length, h / 2],
                [0, 0, 1]
            ])
            
            # Distortion coefficients
            dist_matrix = np.zeros((4, 1), dtype=np.float64)
            
            # Solve PnP to get rotation vector
            success, rotation_vec, translation_vec = cv2.solvePnP(
                self.FACE_3D_MODEL,
                face_2d,
                cam_matrix,
                dist_matrix
            )
            
            if success:
                # Convert rotation vector to rotation matrix
                rotation_matrix, _ = cv2.Rodrigues(rotation_vec)
                
                # Calculate Euler angles
                angles = rotation_matrix_to_angles(rotation_matrix)
                x_axis, y_axis, z_axis = angles
                
                self.state = HeadTrackingState(
                    is_present=True,
                    x_axis=float(x_axis),
                    y_axis=float(y_axis),
                    z_axis=float(z_axis),
                )
                
                # Overlay pose information on the image
                for i, (label, value) in enumerate([
                    ('x-axis', x_axis),
                    ('y-axis', y_axis),
                    ('z-axis', z_axis)
                ]):
                    text = f'{label}: {int(value)}'
                    cv2.putText(
                        image,
                        text,
                        (20, i * 30 + 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (200, 0, 200),
                        2
                    )
        
        return image, self.state
    
    def close(self):
        """Release Mediapipe resources."""
        if self._face_mesh is not None:
            self._face_mesh.close()
