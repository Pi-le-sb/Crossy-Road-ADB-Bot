"""Latched warning-light stop intent. No inputs, files, training or clearance inference."""
from dataclasses import dataclass
import math


def is_warning(obj):
    return obj.source=='primary' and obj.name.strip().lower()=='train_light_on'


def predict_with_warning(frame,primary,obstacles,primary_conf=.25,obstacle_conf=.10,imgsz=640,compute='cpu',obstacle_iou=.5,warning_conf=.10,predictor=None):
    if not all(math.isfinite(v) and 0<v<=1 for v in (primary_conf,warning_conf)):
        raise ValueError('Confidence thresholds must be finite and in (0,1]')
    if predictor is None:
        from dual_model_fusion import predict_both
        predictor = predict_both
    objects = predictor(frame,primary,obstacles,primary_conf=min(primary_conf,warning_conf),
                        obstacle_conf=obstacle_conf,imgsz=imgsz,compute=compute,obstacle_iou=obstacle_iou)
    # Lower the original-model extraction threshold only for the warning class.
    return [o for o in objects if o.source!='primary' or o.confidence>=(warning_conf if is_warning(o) else primary_conf)]


@dataclass(frozen=True)
class RailDecision:
    state: str
    stop_requested: bool
    crossing_clear: bool = False


class RailWarningLatch:
    def __init__(self,threshold=.10):
        if not math.isfinite(threshold) or not 0<threshold<=1: raise ValueError('Invalid warning confidence')
        self.threshold = threshold
        self.latched = False

    def update(self,objects,frame_ok=True):
        if frame_ok and any(is_warning(o) and math.isfinite(o.confidence) and o.confidence>=self.threshold for o in objects):
            self.latched = True
        if self.latched: return RailDecision('HALT_WARNING_LATCHED',True)
        if not frame_ok: return RailDecision('HALT_FRAME_UNKNOWN',True)
        # No detection is NOT proof that a crossing is clear.
        return RailDecision('UNKNOWN_NO_WARNING_DETECTED',False)
