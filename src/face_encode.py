"""
face_encode.py

Detects face(s) in an image and produces a 128-dimensional encoding for
each, using the `face_recognition` library (a wrapper around dlib's
ResNet-based face recognition model).
"""
from pathlib import Path
import face_recognition


class NoFaceFoundError(Exception):
    pass


class MultipleFacesError(Exception):
    pass


def load_and_encode(image_path: str, allow_multiple: bool = False):
    """
    Load an image and return encodings for the face(s) found in it.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = face_recognition.load_image_file(str(path))
    locations = face_recognition.face_locations(image, model="hog")

    if len(locations) == 0:
        raise NoFaceFoundError(f"No face detected in {image_path}")
    if len(locations) > 1 and not allow_multiple:
        raise MultipleFacesError(
            f"{len(locations)} faces detected in {image_path}; "
            "pass --allow-multiple to process all of them"
        )

    encodings = face_recognition.face_encodings(image, known_face_locations=locations)

    return [
        {"encoding": enc, "location": loc}
        for loc, enc in zip(locations, encodings)
    ]