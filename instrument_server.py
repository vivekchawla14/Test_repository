import traceback
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from automation import Automation
# near top
from automate_alignment import AlignmentAutomation

app = Flask(__name__)
auto = Automation()

API_TOKEN = "SuperSecret_Token_41126est"

ALLOWED_SHARED_ROOT = Path(
    r"C:\Users\Public\Documents\Nanomechanics\Profiles\Shared AENI"
).resolve()
ALLOWED_SHARED_ROOT.mkdir(parents=True, exist_ok=True)

LAST_EXPORT = {
    "path": None,
    "name": None,
    "format": None,
}


ALLOWED_ALIGNMENT_METHODS = {
    "automate_alignment_area1",
}

ALIGNMENT_OBJECTS = {}

def check_auth(req):
    token = req.headers.get("X-API-Token", "")
    return token == API_TOKEN

def json_error(message, code=400, traceback_text=None):
    payload = {"status": "error", "message": message}
    if traceback_text:
        payload["traceback"] = traceback_text
    return jsonify(payload), code

def is_under_shared_root(path_like) -> bool:
    p = Path(path_like).resolve()
    return ALLOWED_SHARED_ROOT == p or ALLOWED_SHARED_ROOT in p.parents

def normalize_export_format(export_format: str) -> str:
    fmt = str(export_format).strip().lower()
    return "csv" if fmt == "csv" else "excel"

def find_exported_file(export_dir: str, export_file_name: str, export_format: str):
    export_dir_path = Path(export_dir).resolve()

    if not is_under_shared_root(export_dir_path):
        raise ValueError(f"Export directory is outside allowed shared root: {export_dir_path}")

    if not export_dir_path.exists():
        raise FileNotFoundError(f"Export directory does not exist: {export_dir_path}")

    fmt = normalize_export_format(export_format)
    allowed_exts = [".csv"] if fmt == "csv" else [".xlsx", ".xls"]

    matches = []
    for p in export_dir_path.iterdir():
        if not p.is_file():
            continue
        if p.stem.lower() == str(export_file_name).strip().lower() and p.suffix.lower() in allowed_exts:
            matches.append(p)

    if not matches:
        return None

    return max(matches, key=lambda p: p.stat().st_mtime)


# def automate_alignment_area1(self):
#     r = self.session.post(
#         f"{self.base_url}/automate_alignment_area1",
#         timeout=self.timeout,
#     )
#     r.raise_for_status()
#     return r.json()

# Only expose methods you explicitly approve
ALLOWED_AUTO_METHODS = {
    "process_review_file",
    "apply_review_parameters_ui",
    "click_review_button",
    "open_sample_from_directory",
    "save_review_file_as",
    "move",
    "move_in_increments",
    "starting_tests",
    "start_test_normal",
    "get_current_sample_and_test_ocr",
    "capture_video_panel",
    "change_method",
    "focus",
    "align_focus",
    "engage",
    "set_extension",
    "get_all_ui_state",
    "get_xyz_positions",

}
ALLOWED_AUTO_METHODS.add("capture_video_panel_remote")
ALLOWED_AUTO_METHODS.add("align_focus_remote")
ALLOWED_AUTO_METHODS.add("get_current_sample_and_test_ocr_passive")

@app.route("/ping", methods=["GET"])
def ping():
    if not check_auth(request):
        return json_error("Unauthorized", 401)
    return jsonify({
        "status": "ok",
        "message": "Instrument server reachable",
        "shared_root": str(ALLOWED_SHARED_ROOT),
    })

@app.route("/call_auto", methods=["POST"])
def call_auto():
    if not check_auth(request):
        return json_error("Unauthorized", 401)

    data = request.get_json(force=True)
    method_name = data.get("method")
    args = data.get("args", [])
    kwargs = data.get("kwargs", {})

    if not method_name:
        return json_error("method is required", 400)

    if method_name not in ALLOWED_AUTO_METHODS:
        return json_error(f"Method not allowed: {method_name}", 403)

    try:
        method = getattr(auto, method_name, None)
        if method is None or not callable(method):
            return json_error(f"Automation method not found/callable: {method_name}", 404)

        result = method(*args, **kwargs)

        # If this was process_review_file, try to record the export
        if method_name == "process_review_file":
            export_dir = kwargs.get("export_dir")
            export_file_name = kwargs.get("export_file_name")
            export_format = kwargs.get("export_format", "excel")

            if export_dir and export_file_name:
                exported_file = find_exported_file(export_dir, export_file_name, export_format)
                if exported_file is not None:
                    LAST_EXPORT["path"] = str(exported_file)
                    LAST_EXPORT["name"] = exported_file.name
                    LAST_EXPORT["format"] = normalize_export_format(export_format)

        return jsonify({
            "status": "ok",
            "method": method_name,
            "result": result,
        })

    except Exception as e:
        return json_error(str(e), 400, traceback.format_exc())

@app.route("/last_export", methods=["GET"])
def last_export():
    if not check_auth(request):
        return json_error("Unauthorized", 401)

    if LAST_EXPORT["path"] is None:
        return json_error("No export recorded yet", 404)

    return jsonify({
        "status": "ok",
        "path": LAST_EXPORT["path"],
        "name": LAST_EXPORT["name"],
        "format": LAST_EXPORT["format"],
    })

@app.route("/download_last_export", methods=["GET"])
def download_last_export():
    if not check_auth(request):
        return json_error("Unauthorized", 401)

    export_path = LAST_EXPORT["path"]
    if export_path is None:
        return json_error("No export recorded yet", 404)

    p = Path(export_path).resolve()
    if not p.exists():
        return json_error(f"Last export file no longer exists: {p}", 404)

    if not is_under_shared_root(p):
        return json_error("Refusing to serve file outside shared root", 403)

    return send_file(str(p), as_attachment=True, download_name=p.name)

@app.route("/download_file", methods=["POST"])
def download_file():
    if not check_auth(request):
        return json_error("Unauthorized", 401)

    data = request.get_json(force=True)
    directory = data.get("directory")
    filename = data.get("filename")

    if not directory or not filename:
        return json_error("directory and filename required", 400)

    try:
        dir_path = Path(directory).resolve()
        file_path = (dir_path / filename).resolve()

        if not is_under_shared_root(dir_path):
            return json_error(f"Directory outside shared root: {dir_path}", 403)

        if not file_path.exists():
            return json_error(f"File not found: {file_path}", 404)

        if not file_path.is_file():
            return json_error(f"Not a file: {file_path}", 400)

        if not is_under_shared_root(file_path):
            return json_error("Refusing to serve file outside shared root", 403)

        return send_file(str(file_path), as_attachment=True, download_name=file_path.name)

    except Exception as e:
        return json_error(str(e), 400, traceback.format_exc())
    
@app.route("/move_to_aligned_point", methods=["POST"])
def move_to_aligned_point():
    if not check_auth(request):
        return json_error("Unauthorized", 401)

    try:
        data = request.get_json(force=True)
        area_name = data["area_name"]
        x = float(data["x"])
        y = float(data["y"])
        plane_params = data.get("plane_params", None)

        if area_name not in ALIGNMENT_OBJECTS:
            return json_error(f"No alignment object found for {area_name}", 400)

        aligner = ALIGNMENT_OBJECTS[area_name]
        aligner.move_to_points([(x, y)], params=plane_params)

        return jsonify({
            "status": "ok",
            "area_name": area_name,
            "x": x,
            "y": y,
            "plane_params": plane_params,
        })

    except Exception as e:
        return json_error(str(e), 400, traceback.format_exc())

@app.route("/restore_alignment", methods=["POST"])
def restore_alignment():
    if not check_auth(request):
        return json_error("Unauthorized", 401)

    try:
        data = request.get_json(force=True)

        area_name = data["area_name"]
        macro_image_path = data.get("macro_image_path", None)
        macro_scale_x = float(data["macro_scale_x"])
        macro_scale_y = float(data["macro_scale_y"])

        new_origin_macro = tuple(data["new_origin_macro"])
        new_origin_micro = tuple(data["new_origin_micro"])

        alignment_auto = AlignmentAutomation(
            macro_image_path=macro_image_path,
            macro_scale_x=macro_scale_x,
            macro_scale_y=macro_scale_y,
        )

        alignment_auto.new_origin_macro = new_origin_macro
        alignment_auto.new_origin_micro = new_origin_micro

        ALIGNMENT_OBJECTS[area_name] = alignment_auto

        return jsonify({
            "status": "ok",
            "area_name": area_name,
            "new_origin_macro": new_origin_macro,
            "new_origin_micro": new_origin_micro,
            "macro_scale_x": macro_scale_x,
            "macro_scale_y": macro_scale_y,
        })

    except Exception as e:
        return json_error(str(e), 400, traceback.format_exc())


@app.route("/move_to_aligned_point_abs", methods=["POST"])
def move_to_aligned_point_abs():
    if not check_auth(request):
        return json_error("Unauthorized", 401)

    try:
        data = request.get_json(force=True)

        area_name = data["area_name"]
        x = float(data["x"])
        y = float(data["y"])
        plane_params = data.get("plane_params", None)

        if area_name not in ALIGNMENT_OBJECTS:
            return json_error(f"No alignment object found for {area_name}", 400)

        aligner = ALIGNMENT_OBJECTS[area_name]

        ox_macro, oy_macro = aligner.new_origin_macro
        ox_micro, oy_micro = aligner.new_origin_micro

        sx = float(aligner.alignment.macro_scale_x)
        sy = float(aligner.alignment.macro_scale_y)

        current_x, current_y, current_z = auto.get_xyz_positions()

        target_x = ox_micro + ((x - ox_macro) / sx)
        target_y = oy_micro + ((y - oy_macro) / sy)

        dx = target_x - current_x
        dy = target_y - current_y

        if abs(dx) > 0.01:
            auto.move(abs(dx), "right" if dx > 0 else "left")

        if abs(dy) > 0.01:
            auto.move(abs(dy), "down" if dy > 0 else "up")

        if plane_params is not None:
            auto.focus(plane_params)

        final_x, final_y, final_z = auto.get_xyz_positions()

        return jsonify({
            "status": "ok",
            "area_name": area_name,
            "input_pixel": [x, y],
            "target_xy": [target_x, target_y],
            "start_xyz": [current_x, current_y, current_z],
            "final_xyz": [final_x, final_y, final_z],
            "move_dxdy": [dx, dy],
        })

    except Exception as e:
        return json_error(str(e), 400, traceback.format_exc())


@app.route("/automate_alignment_" \
"area1", methods=["POST"])
def automate_alignment_area1():
    if not check_auth(request):
        return json_error("Unauthorized", 401)

    try:
        if "macro_image" not in request.files:
            return json_error("macro_image file is required", 400)

        macro_file = request.files["macro_image"]

        upload_dir = ALLOWED_SHARED_ROOT / "alignment_uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)

        macro_path = upload_dir / macro_file.filename
        macro_file.save(str(macro_path))

        macro_scale_x = float(request.form.get("macro_scale_x", 0.1556))
        macro_scale_y = float(request.form.get("macro_scale_y", 0.1556))
        area_name = request.form.get("area_name", "Area1")

        alignment_auto = AlignmentAutomation(
            macro_image_path=str(macro_path),
            macro_scale_x=macro_scale_x,
            macro_scale_y=macro_scale_y,
        )

        rotated_image = alignment_auto.automate_alignment()

        ALIGNMENT_OBJECTS[area_name] = alignment_auto

        
    
        return jsonify({
            "status": "ok",
            "area_name": area_name,
            "macro_image_path": str(macro_path),
            "new_origin_macro": alignment_auto.new_origin_macro,
            "new_origin_micro": alignment_auto.new_origin_micro,
            "small_image_angle": alignment_auto.small_image_angle,
            "big_image_angle": alignment_auto.big_image_angle,
            "rotation_angle": alignment_auto.rotation_angle,
        })

    except Exception as e:
        return json_error(str(e), 400, traceback.format_exc())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)