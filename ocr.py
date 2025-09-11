import json
import cv2
import numpy as np
import onnxruntime as ort

from preprocess import segment_image  # Your segmentation script

# ----------------------------
# OCR Engine Class
# ----------------------------
class OCR:
    def __init__(self, settings=None, bg_gray=50, data_directory="OCR", debug_path="debug"):
        self.data_directory = data_directory
        self.onnx_path = f"{data_directory}/STARDUST.onnx"
        self.mapping_dir = f"{data_directory}/mapping.json"
        self.debug_path = debug_path
        self.bg_gray = bg_gray

        if settings is not None:
            self.settings = settings
        else:
            self.settings = self.load_default_settings()

        # Load mapping
        with open(self.mapping_dir, "r") as f:
            folder_to_char = json.load(f)
        self.char_list = sorted(folder_to_char.values())
        self.label_to_char = {i: c for i, c in enumerate(self.char_list)}

        # Load ONNX model
        self.ort_session = ort.InferenceSession(self.onnx_path, providers=["CPUExecutionProvider"])


    def load_default_settings(self):
        return {
            'verbose': 1,
            'custom_width': False,
            'width_small': 6,
            'width_medium': 7,
            'width_large': 8,
            'save_images': False,
            'existing_weapon': True,
            'theme': 'dark',
        }

    def preprocess_char(self, char_img) -> tuple[np.ndarray, np.ndarray]:
        """Pads a character image to 32x32 and converts to normalized (1,1,32,32) array for ONNX."""
        H, W = char_img.shape
        canvas = np.full((32, 32), self.bg_gray, dtype=np.uint8)
        y_off = (32 - H) // 2
        x_off = (32 - W) // 2
        canvas[y_off:y_off+H, x_off:x_off+W] = char_img

        # Normalize to [0,1], add channel + batch dims
        x = canvas.astype(np.float32) / 255.0
        x = np.expand_dims(x, axis=(0, 1))  # shape (1, 1, 32, 32)

        return x, canvas

    def ocr_segmented(self, img, settings=None) -> str:
        """Runs OCR on a segmented image."""
        settings = settings or self.settings

        debug_path = self.debug_path if settings.get('save_images', False) else None
        lines = segment_image(img, data_directory=self.data_directory, debug_path=debug_path, settings=settings)

        results: list[str] = []
        for line_idx, chars in enumerate(lines):
            line_str = ""
            for charnum, char_img in enumerate(chars):
                if not np.any(char_img != self.bg_gray):
                    line_str += " "
                    continue

                x, preprocessed_img = self.preprocess_char(char_img)
                input_name = self.ort_session.get_inputs()[0].name
                outputs = self.ort_session.run(None, {input_name: x})
                output_arr = np.array(outputs[0])
                pred_idx = int(np.argmax(output_arr, axis=1)[0])
                line_str += self.label_to_char[pred_idx]

            results.append(line_str)

        if settings.get('verbose', 0) > 0:
            print("OCR Results:")
            print("\n".join(results))

        return "\n".join(results)


# ----------------------------
# Standalone Function
# ----------------------------
def run_ocr(img, dataset_dir="OCR", debug_path="debug"):
    settings = {
        'save_images': False,
        'verbose': 0
    }
    ocr_engine = OCR(data_directory=dataset_dir, debug_path=debug_path)
    return ocr_engine.ocr_segmented(img, settings=settings)


# ----------------------------
# CLI
# ----------------------------
if __name__ == "__main__":
    import sys

    img_path = "weapon.png"
    if len(sys.argv) > 1:
        img_path = sys.argv[1]

    image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print(f"Error: Could not load image from '{img_path}'. Check the file path.")
        sys.exit(1)

    results = run_ocr(image)

    print("=== OCR RESULT ===")
    print(results)
