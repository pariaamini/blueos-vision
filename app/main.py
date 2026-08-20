#!/usr/bin/env python3

import logging.handlers
import time
from pathlib import Path

import requests
from litestar import Litestar, MediaType, get
from litestar.controller import Controller
from litestar.datastructures import State
from litestar.logging import LoggingConfig
from litestar.static_files.config import StaticFilesConfig


class CountController(Controller):
    COUNT_VAR = "quickstart_backend_perm_count"

    def __init__(self, *args, **kwargs):
        self._temp_count = 0
        super().__init__(*args, **kwargs)

    @get("/temp_count", sync_to_thread=False)
    def increment_temp_count(self) -> dict[str, int]:
        self._temp_count += 1
        return {"value": self._temp_count}

    @get("/persistent_count", sync_to_thread=True)
    def increment_persistent_count(self, state: State) -> dict[str, int]:
        try:
            response = requests.get(
                f"{state.bag_url}/get/{self.COUNT_VAR}",
                timeout=5,
            )
            response.raise_for_status()
            value = response.json()["value"]
        except Exception:
            value = 0

        value += 1
        output = {"value": value}

        requests.post(
            f"{state.bag_url}/set/{self.COUNT_VAR}",
            json=output,
            timeout=5,
        )
        return output


class CoralController(Controller): 
    MODEL_PATH = Path(
        "/app/test_data/"
        "ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite"
    )
    LABELS_PATH = Path("/app/test_data/coco_labels.txt")
    IMAGE_PATH = Path("/app/test_data/grace_hopper.bmp")

    @get("/test_coral", media_type=MediaType.JSON, sync_to_thread=True)
    def test_coral(self) -> dict:
        try:
            from PIL import Image
            from pycoral.adapters import common, detect
            from pycoral.utils.dataset import read_label_file
            from pycoral.utils.edgetpu import make_interpreter

            labels = read_label_file(str(self.LABELS_PATH))
            interpreter = make_interpreter(str(self.MODEL_PATH))
            interpreter.allocate_tensors()

            image = Image.open(self.IMAGE_PATH).convert("RGB")
            _, scale = common.set_resized_input(
                interpreter,
                image.size,
                lambda size: image.resize(
                    size,
                    Image.Resampling.LANCZOS,
                ),
            )

            inference_times_ms = []

            # Run several times so we can see the slower first inference
            # separately from subsequent Coral inference times.
            for _ in range(5):
                start = time.perf_counter()
                interpreter.invoke()
                inference_times_ms.append(
                    round((time.perf_counter() - start) * 1000, 2)
                )

            objects = detect.get_objects(
                interpreter,
                score_threshold=0.4,
                image_scale=scale,
            )

            detections = [
                {
                    "label": labels.get(obj.id, str(obj.id)),
                    "class_id": obj.id,
                    "confidence": round(float(obj.score), 3),
                    "bounding_box": [
                        int(obj.bbox.xmin),
                        int(obj.bbox.ymin),
                        int(obj.bbox.xmax),
                        int(obj.bbox.ymax),
                    ],
                }
                for obj in objects
            ]

            return {
                "success": True,
                "coral_connected": True,
                "model": self.MODEL_PATH.name,
                "image": self.IMAGE_PATH.name,
                "inference_times_ms": inference_times_ms,
                "detections": detections,
            }

        except Exception as error:
            return {
                "success": False,
                "coral_connected": False,
                "error_type": type(error).__name__,
                "error": str(error),
            }


logging_config = LoggingConfig(
    loggers={
        __name__: {
            "level": "INFO",
            "handlers": ["queue_listener"],
        }
    },
)

log_dir = Path("/app/logs")
log_dir.mkdir(parents=True, exist_ok=True)

file_handler = logging.handlers.RotatingFileHandler(
    log_dir / "blueos-vision.log",
    maxBytes=2**16,
    backupCount=1,
)

app = Litestar(
    route_handlers=[CountController, CoralController],
    state=State(
        {
            "bag_url": "http://host.docker.internal/bag/v1.0",
        }
    ),
    static_files_config=[
        StaticFilesConfig(
            directories=["app/static"],
            path="/",
            html_mode=True,
        )
    ],
    logging_config=logging_config,
)

app.logger.addHandler(file_handler)