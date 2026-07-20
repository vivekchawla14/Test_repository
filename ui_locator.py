# ui_locator.py

import re
from typing import Dict, Optional, Any, List

from pywinauto import Desktop


class InViewUILocator:
    """
    Central UI locator for:
    1. fixed-position main/review/method controls
    2. popup/dialog discovery using pywinauto
    3. system-state reading from static controls
    """

    REVIEW_PARAMETERS_EH = {
        "poissons ratio": [325, 620],
        "Drift": [325, 640],
        "Min Depth for Results": [325, 652],
        "Cite at Depth or Load": [325, 672],
        "Stiffness for Contact": [325, 695],
        "Depth to Cite Results (nm)": [325, 710],
        "Load to cite Results (mN)": [325, 735],
        "Metal : Pile up (0) or No Pile Up (1)": [325, 760],
        "Test is Valid": [325, 787],
    }

    REVIEW_PARAMETERS_CONSTANT = {
        "poissons ratio": [325, 611],
        "Drift": [325, 632],
        "Detph to End Average": [325, 652],
        "Depth to Start Average": [325, 669],
    }

    IN_VIEW_CONSTANT_DISP_METHOD = {
        "target load": [1850, 317],
        "target depth": [1848, 347],
        "target displacement rate": [1848, 380],
        "Hold Maximum load time": [1848, 416],
        "Target Unload Time": [1848, 440],
        "Data acq rate": [1848, 465],
    }

    IN_VIEW_EH_METHOD = {
        "poisson": [1848, 232],
        "drift": [1848, 259],
        "metal": [1848, 293],
        "target load": [1848, 385],
        "target depth": [1848, 416],
        "surface approach distance": [1848, 446],
        "surface approach velocity": [1848, 475],
        "Strain rate": [1848, 503],
        

    }

    OFFSET_REVIEW = {
        "System": [35, 33],
        "Sample File": [108, 33],
        "Recent Sample": [119, 58],
        "Open Sample": [119, 76],
        "Sample_Save": [119, 98],
        "Sample_Save As": [119, 125],
        "Sample_recalculate": [119, 142],
        "Sample_Export": [119, 193],
        "Sample_Export_csv": [276, 194],
        "Sample_Export_excel": [276, 218],
        "Method File": [179, 33],
        "Recent Methods": [203, 54],
        "Method_open": [203, 77],
        "Method_save": [203, 97],
        "Method_save as": [203, 123],
        "Method_edit": [203, 143],
        "New Data Available": [403, 60]
        
    }

    OFFSET_INVIEW = {
        "System": [35, 33],
        "Sample File": [108, 33],
        "Recent Sample": [119, 58],
        "Open Sample": [119, 76],
        "Sample_Save": [119, 98],
        "Sample_Save As": [119, 125],
        "Method File": [179, 33],
        "Recent Methods": [203, 54],
        "Method_open": [203, 77],
        "Method_save": [203, 97],
        "Method_save as": [203, 123],
        "Method_edit": [203, 143],
        "View": [246, 33],
        "Add Control": [306, 33],
        "Add_control_extention": [331, 63],
        "Add_control_xyposition": [331, 76],
        "Help": [372, 33],
        

        "array": [1446, 545],
        "add_indent": [1604, 544],
        "subtract": [1543, 545],
        "clear all": [1582, 545],
        "add_ok": [844, 642],
        "add_cancel": [935, 642],
        "add_xindents": [893, 432],
        "add_yindents": [907, 462],
        "add_xspacing": [910, 525],
        "add_yspacing": [910, 550],
        "add_rotation": [927, 595],
        "add_import": [1032, 643],

        "diagonal_bbox1": [8, 422],
        "diagonal_bbox2": [212, 1020],
        "Puck 1": [116, 178],
        "Puck 2": [116, 278],
        "load_sample_tray": [124, 352],

        "Z_control": [1457, 1028],
        "Displacement in Z": [1672, 703],
        "Displacement in Z set": [1767, 703],
        "Engage in Z": [1578, 840],
        "Engage in Z set": [1744, 839],
        "XY_control": [1542, 1028],
        "engage": [1753, 789],

        "right click location": [829, 568],
        "remove backlash": [889, 563],
        "move relative": [897, 579],

        "Test_name_loc": [1478, 272],
        "Cancel": [1777, 546],
        "Continue": [1867, 546],
        "Sample_name":[1514,219],
        "Add":[1600, 546],
        "edit": [1682, 546],
        "remove": [1763, 544],
        "clear_all": [1874, 547],

        "start": [1773, 74],
        "stop": [1773, 74],

        "Method_control_settings":[23,406],
        "select_meters":[80, 432],
        
        "x_value_now":[699, 515],
        "y_value_now":[699, 515],
        "put_on_right":[947, 482],
        "close_list_box":[958, 694],
        
    }

    def __init__(
        self,
        inview_title: str = "InView RunTest-inForce1000",
        review_title_contains: str = "InView ReviewData",
        open_dialog_title: str = "Open",
        indent_array_title: str = "Generate Indent Array",
        Save_As: str = "Save As",
    ):
        self.inview_title = inview_title
        self.review_title_contains = review_title_contains
        self.open_dialog_title = open_dialog_title
        self.indent_array_title = indent_array_title
        self.desktop = Desktop(backend="win32")
        self.Save_As_title= Save_As

    @staticmethod
    def rect_to_dict(rect) -> Dict[str, int]:
        return {
            "left": rect.left,
            "top": rect.top,
            "right": rect.right,
            "bottom": rect.bottom,
            "width": rect.width(),
            "height": rect.height(),
            "center_x": (rect.left + rect.right) // 2,
            "center_y": (rect.top + rect.bottom) // 2,
        }

    @staticmethod
    def _norm(s: str) -> str:
        return s.strip().lower()

    @staticmethod
    def _is_numeric_text(s: str) -> bool:
        s = s.strip()
        if not s:
            return False
        if s.lower() == "nan":
            return True
        return re.fullmatch(r"[+-]?\d+(?:\.\d+)?", s) is not None

    def get_dialog_exact(self, title: str, timeout: int = 10):
        dlg = self.desktop.window(title=title)
        dlg.wait("exists", timeout=timeout)
        dlg.wait("visible", timeout=timeout)
        return dlg

    def get_dialog_best_review(self, timeout: int = 10):
        dlg = self.desktop.window(title_re=f".*{re.escape(self.review_title_contains)}.*")
        dlg.wait("exists", timeout=timeout)
        dlg.wait("visible", timeout=timeout)
        return dlg

    def get_inview_dialog(self, timeout: int = 10):
        return self.get_dialog_exact(self.inview_title, timeout=timeout)

    def get_open_dialog(self, timeout: int = 10):
        return self.get_dialog_exact(self.open_dialog_title, timeout=timeout)
    
    def get_saveas_dialog(self, timeout: int = 10):
        return self.get_dialog_exact(self.Save_As_title, timeout=timeout)


    def get_indent_array_dialog(self, timeout: int = 10):
        return self.get_dialog_exact(self.indent_array_title, timeout=timeout)

    def get_all_controls(self, dlg) -> List[Dict[str, Any]]:
        rows = []
        for ctrl in dlg.descendants():
            try:
                rect = ctrl.rectangle()
                rows.append({
                    "text": ctrl.window_text().strip(),
                    "class": ctrl.class_name(),
                    "id": ctrl.control_id(),
                    "rect_obj": rect,
                    "rect": self.rect_to_dict(rect),
                    "ctrl": ctrl,
                })
            except Exception:
                pass
        return rows

    def get_inview_button(self, name: str) -> List[int]:
        if name not in self.OFFSET_INVIEW:
            raise KeyError(f"InView button '{name}' not defined")
        return self.OFFSET_INVIEW[name]

    def get_review_button(self, name: str) -> List[int]:
        if name not in self.OFFSET_REVIEW:
            raise KeyError(f"Review button '{name}' not defined")
        return self.OFFSET_REVIEW[name]

    def get_method_field(self, method_type: str, name: str) -> List[int]:
        method_type = self._norm(method_type)
        if method_type in ["eh", "erik", "eh_method"]:
            table = self.IN_VIEW_EH_METHOD
        elif method_type in ["constant", "constant_disp", "constant displacement"]:
            table = self.IN_VIEW_CONSTANT_DISP_METHOD
        else:
            raise ValueError(f"Unknown method type: {method_type}")

        if name not in table:
            raise KeyError(f"Method field '{name}' not defined in '{method_type}'")
        return table[name]

    def get_review_parameter(self, review_type: str, name: str) -> List[int]:
        review_type = self._norm(review_type)
        name_norm = self._norm(name)

        if review_type == "eh":
            table = self.REVIEW_PARAMETERS_EH
        elif review_type == "constant":
            table = self.REVIEW_PARAMETERS_CONSTANT
        else:
            raise ValueError(f"Unknown review type: {review_type}")

        # build normalized lookup table once per call
        norm_table = {self._norm(k): v for k, v in table.items()}

        if name_norm not in norm_table:
            raise KeyError(f"Review parameter '{name}' not defined in '{review_type}'")

        return norm_table[name_norm]

    def find_open_dialog_controls(self) -> Dict[str, Optional[Dict[str, Any]]]:
        dlg = self.get_open_dialog()
        rows = self.get_all_controls(dlg)

        edits = []
        for r in rows:
            if "EDIT" in r["class"].upper():
                if r["rect"]["width"] > 30 and r["rect"]["height"] > 10:
                    edits.append(r)

        edits.sort(key=lambda r: (r["rect"]["top"], r["rect"]["left"]))

        address_edit = None
        file_edit = None
        open_btn = None
        cancel_btn = None

        top_candidates = [e for e in edits if e["rect"]["top"] < 150]
        if top_candidates:
            address_edit = sorted(top_candidates, key=lambda e: e["rect"]["width"], reverse=True)[0]

        bottom_candidates = [e for e in edits if e["rect"]["top"] > 500]
        if bottom_candidates:
            file_edit = sorted(bottom_candidates, key=lambda e: e["rect"]["width"], reverse=True)[0]

        for r in rows:
            txt = self._norm(r["text"])
            cls = r["class"].upper()
            if "BUTTON" not in cls:
                continue
            if txt in ["open", "&open"]:
                open_btn = r
            elif txt in ["cancel", "&cancel"]:
                cancel_btn = r

        return {
            "address_bar": address_edit,
            "file_name": file_edit,
            "open_button": open_btn,
            "cancel_button": cancel_btn,
            "all_edits": edits,
        }
    
    def find_saveas_dialog_controls(self) -> Dict[str, Optional[Dict[str, Any]]]:
        dlg = self.get_saveas_dialog()
        rows = self.get_all_controls(dlg)

        edits = []
        for r in rows:
            if "EDIT" in r["class"].upper():
                if r["rect"]["width"] > 30 and r["rect"]["height"] > 10:
                    edits.append(r)

        edits.sort(key=lambda r: (r["rect"]["top"], r["rect"]["left"]))

        address_edit = None
        file_edit = None
        save_btn = None
        cancel_btn = None

        top_candidates = [e for e in edits if e["rect"]["top"] < 150]
        if top_candidates:
            address_edit = sorted(top_candidates, key=lambda e: e["rect"]["width"], reverse=True)[0]

        bottom_candidates = [e for e in edits if e["rect"]["top"] > 500]
        if bottom_candidates:
            file_edit = sorted(bottom_candidates, key=lambda e: e["rect"]["width"], reverse=True)[0]

        for r in rows:
            txt = self._norm(r["text"])
            cls = r["class"].upper()
            if "BUTTON" not in cls:
                continue
            if txt in ["save", "&save"]:
                save_btn = r
            elif txt in ["cancel", "&cancel"]:
                cancel_btn = r

        return {
            "address_bar": address_edit,
            "file_name": file_edit,
            "save_button": save_btn,
            "cancel_button": cancel_btn,
            "all_edits": edits,
        }

    def find_relative_move_controls(self) -> Optional[Dict[str, Any]]:
        dlg = self.get_inview_dialog()
        rows = self.get_all_controls(dlg)

        labels = [r for r in rows if self._norm(r["text"]) == "relative move"]
        if not labels:
            return None

        label = labels[0]
        lx = label["rect"]["left"]
        ly_bottom = label["rect"]["bottom"]

        edit_candidates = []
        for r in rows:
            if "EDIT" not in r["class"].upper():
                continue
            if r["rect"]["top"] >= ly_bottom - 5:
                dx = abs(r["rect"]["left"] - lx)
                dy = r["rect"]["top"] - ly_bottom
                score = dx + abs(dy)
                edit_candidates.append((score, r))

        best_edit = None
        if edit_candidates:
            edit_candidates.sort(key=lambda x: x[0])
            best_edit = edit_candidates[0][1]

        result = {
            "label": label,
            "edit": best_edit,
        }

        if best_edit is not None:
            result["widget_box"] = self._build_relative_move_box(label, best_edit)
        else:
            result["widget_box"] = None

        return result

    def _build_relative_move_box(self, label_info, edit_info) -> Dict[str, int]:
        label = label_info["rect"]
        edit = edit_info["rect"]

        left = edit["left"] - 5
        top = label["top"] - 20
        right = edit["right"] + 150
        bottom = edit["bottom"] + 40

        return {
            "left": left,
            "top": top,
            "right": right,
            "bottom": bottom,
            "width": right - left,
            "height": bottom - top,
            "center_x": (left + right) // 2,
            "center_y": (top + bottom) // 2,
        }

    def get_relative_move_arrow_position(self, direction: str) -> List[int]:
        rel = self.find_relative_move_controls()
        if rel is None or rel["widget_box"] is None:
            raise RuntimeError("Relative Move widget not found")

        box = rel["widget_box"]

        positions = {
            "left": (0.68, 0.54),
            "up": (0.78, 0.35),
            "right": (0.92, 0.54),
            "down": (0.80, 0.81),
            "center": (0.80, 0.54),
        }

        if direction not in positions:
            raise ValueError(f"Unknown direction '{direction}'")

        rx, ry = positions[direction]
        x = int(box["left"] + rx * box["width"])
        y = int(box["top"] + ry * box["height"])
        return [x, y]

    def find_indent_array_controls(self) -> Dict[str, Any]:
        dlg = self.get_indent_array_dialog()
        rows = self.get_all_controls(dlg)

        labels = [r for r in rows if "STATIC" in r["class"].upper() and r["text"].strip()]
        edits = [r for r in rows if "EDIT" in r["class"].upper()]
        buttons = [r for r in rows if "BUTTON" in r["class"].upper()]

        edits.sort(key=lambda r: (r["rect"]["top"], r["rect"]["left"]))

        def find_label(target_text: str):
            for r in labels:
                if self._norm(r["text"]) == self._norm(target_text):
                    return r
            return None

        def find_edit_to_right(label_text: str, max_dx: int = 250, max_dy: int = 25):
            label = find_label(label_text)
            if label is None:
                return None

            lx_right = label["rect"]["right"]
            ly_center = label["rect"]["center_y"]

            best = None
            best_score = None

            for e in edits:
                ex_left = e["rect"]["left"]
                ey_center = e["rect"]["center_y"]
                dx = ex_left - lx_right
                dy = abs(ey_center - ly_center)

                if dx >= 0 and dx <= max_dx and dy <= max_dy:
                    score = dx + dy
                    if best is None or score < best_score:
                        best = e
                        best_score = score

            return best

        def find_button(name: str):
            for b in buttons:
                txt = self._norm(b["text"])
                if txt in [self._norm(name), "&" + self._norm(name)]:
                    return b
            return None

        x_spacing = find_edit_to_right("X Spacing(µm):") or find_edit_to_right("X Spacing(μm):")
        y_spacing = find_edit_to_right("Y Spacing(µm):") or find_edit_to_right("Y Spacing(μm):")


        return {
            "X Indents": find_edit_to_right("X Indents"),
            "Y Indents": find_edit_to_right("Y Indents"),
            "X Spacing": x_spacing,
            "Y Spacing": y_spacing,
            "Rotation": find_edit_to_right("Rotation(deg)"),
            "OK": find_button("OK"),
            "Cancel": find_button("Cancel"),
            "Import": find_button("Import"),
        }

    def get_static_controls(self, dlg=None) -> List[Dict[str, Any]]:
        if dlg is None:
            dlg = self.get_inview_dialog()

        rows = []
        for ctrl in dlg.descendants():
            try:
                cls = ctrl.class_name()
                if "STATIC" in cls.upper():
                    txt = ctrl.window_text()
                    rect = ctrl.rectangle()
                    rows.append({
                        "text": txt.strip(),
                        "class": cls,
                        "rect": rect,
                        "top": rect.top,
                        "left": rect.left,
                        "bottom": rect.bottom,
                    })
            except Exception:
                pass

        rows.sort(key=lambda r: (r["top"], r["left"]))
        return rows

    def _missing_result(
        self,
        label: str,
        reason: str,
        label_rect=None,
        value_text=None,
        value=None,
        unit=None,
        value_rect=None,
        unit_rect=None,
    ) -> Dict[str, Any]:
        return {
            "label": label,
            "status": "missing",
            "reason": reason,
            "value_text": value_text,
            "value": value,
            "unit": unit,
            "label_rect": label_rect,
            "value_rect": value_rect,
            "unit_rect": unit_rect,
        }

    def _nan_result(
        self,
        label: str,
        reason: str,
        label_rect=None,
        value_text="NaN",
        unit=None,
        value_rect=None,
        unit_rect=None,
    ) -> Dict[str, Any]:
        return {
            "label": label,
            "status": "nan",
            "reason": reason,
            "value_text": value_text,
            "value": float("nan"),
            "unit": unit,
            "label_rect": label_rect,
            "value_rect": value_rect,
            "unit_rect": unit_rect,
        }

    def _ok_result(
        self,
        label: str,
        value_text: str,
        value: float,
        unit: str,
        label_rect=None,
        value_rect=None,
        unit_rect=None,
    ) -> Dict[str, Any]:
        return {
            "label": label,
            "status": "ok",
            "reason": None,
            "value_text": value_text,
            "value": value,
            "unit": unit,
            "label_rect": label_rect,
            "value_rect": value_rect,
            "unit_rect": unit_rect,
        }

    def read_metric_simple(
        self,
        rows: List[Dict[str, Any]],
        label: str,
        expected_unit: Optional[str] = None,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ) -> Dict[str, Any]:

        label_norm = self._norm(label)

        idx = None
        for i, r in enumerate(rows):
            if self._norm(r["text"]) == label_norm:
                idx = i
                break

        if idx is None:
            return self._missing_result(label=label, reason="label missing")

        label_row = rows[idx]
        label_left = label_row["left"]

        candidates = rows[idx + 1: idx + 7]
        candidates = [r for r in candidates if abs(r["left"] - label_left) <= 5]

        value_row = None
        unit_row = None

        for j, r in enumerate(candidates):
            if self._is_numeric_text(r["text"]):
                value_row = r
                for k in range(j + 1, len(candidates)):
                    if candidates[k]["text"] and not self._is_numeric_text(candidates[k]["text"]):
                        unit_row = candidates[k]
                        break
                break

        if value_row is None:
            return self._missing_result(
                label=label_row["text"],
                reason="value row missing",
                label_rect=label_row["rect"],
            )

        if unit_row is None:
            if value_row["text"].lower() == "nan":
                return self._nan_result(
                    label=label_row["text"],
                    reason="value displayed as NaN but unit row missing",
                    label_rect=label_row["rect"],
                    value_text=value_row["text"],
                    value_rect=value_row["rect"],
                )
            return self._missing_result(
                label=label_row["text"],
                reason="unit row missing",
                label_rect=label_row["rect"],
                value_text=value_row["text"],
                value=None,
                value_rect=value_row["rect"],
            )

        if expected_unit is not None and unit_row["text"].strip() != expected_unit.strip():
            if value_row["text"].lower() == "nan":
                return self._nan_result(
                    label=label_row["text"],
                    reason=f"unit mismatch: expected {expected_unit}, found {unit_row['text']}",
                    label_rect=label_row["rect"],
                    value_text=value_row["text"],
                    unit=unit_row["text"],
                    value_rect=value_row["rect"],
                    unit_rect=unit_row["rect"],
                )
            return self._missing_result(
                label=label_row["text"],
                reason=f"unit mismatch: expected {expected_unit}, found {unit_row['text']}",
                label_rect=label_row["rect"],
                value_text=value_row["text"],
                value=None,
                unit=unit_row["text"],
                value_rect=value_row["rect"],
                unit_rect=unit_row["rect"],
            )

        txt = value_row["text"]

        if txt.lower() == "nan":
            return self._nan_result(
                label=label_row["text"],
                reason="value displayed as NaN",
                label_rect=label_row["rect"],
                value_text=txt,
                unit=unit_row["text"],
                value_rect=value_row["rect"],
                unit_rect=unit_row["rect"],
            )

        val = float(txt)

        if min_val is not None and val < min_val:
            return self._missing_result(
                label=label_row["text"],
                reason=f"value below minimum: {val} < {min_val}",
                label_rect=label_row["rect"],
                value_text=txt,
                value=val,
                unit=unit_row["text"],
                value_rect=value_row["rect"],
                unit_rect=unit_row["rect"],
            )

        if max_val is not None and val > max_val:
            return self._missing_result(
                label=label_row["text"],
                reason=f"value above maximum: {val} > {max_val}",
                label_rect=label_row["rect"],
                value_text=txt,
                value=val,
                unit=unit_row["text"],
                value_rect=value_row["rect"],
                unit_rect=unit_row["rect"],
            )

        return self._ok_result(
            label=label_row["text"],
            value_text=txt,
            value=val,
            unit=unit_row["text"],
            label_rect=label_row["rect"],
            value_rect=value_row["rect"],
            unit_rect=unit_row["rect"],
        )

    def read_main_state(self) -> Dict[str, Dict[str, Any]]:
        dlg = self.get_inview_dialog()
        rows = self.get_static_controls(dlg)

        return {
            "Extension": self.read_metric_simple(rows, "Extension", expected_unit="mm", min_val=0, max_val=20),
            "Force": self.read_metric_simple(rows, "Force", expected_unit="mN"),
            "Displacement": self.read_metric_simple(rows, "Displacement", expected_unit="nm"),
            "LOAD": self.read_metric_simple(rows, "LOAD", expected_unit="mN"),
            "DEPTH": self.read_metric_simple(rows, "DEPTH", expected_unit="nm"),
            "STIFFNESS": self.read_metric_simple(rows, "STIFFNESS", expected_unit="N/m"),
            "HARDNESS": self.read_metric_simple(rows, "HARDNESS", expected_unit="GPa"),
            "MODULUS": self.read_metric_simple(rows, "MODULUS", expected_unit="GPa"),
            "Temperature": self.read_metric_simple(rows, "Temperature", expected_unit="C"),
            "X Axis Position": self.read_metric_simple(rows, "X Axis Position", expected_unit="µm"),
            "Y Axis Position": self.read_metric_simple(rows, "Y Axis Position", expected_unit="µm"),
        }

    @staticmethod
    def print_metric(name: str, result: Dict[str, Any]):
        status = result["status"]

        if status == "missing":
            print(f"{name}: MISSING")
            if result.get("reason"):
                print(f"  reason = {result['reason']}")
            return

        if status == "nan":
            unit = result["unit"] if result["unit"] is not None else ""
            print(f"{name}: NaN {unit}".rstrip())
            print("  status = nan")
            print(f"  value_rect = {result['value_rect']}")
            return

        print(f"{name}: {result['value_text']} {result['unit']}")
        print("  status = ok")
        print(f"  value_rect = {result['value_rect']}")

    def print_main_state(self):
        state = self.read_main_state()
        print("\n=== MAIN STATE ===")
        for name, result in state.items():
            self.print_metric(name, result)


if __name__ == "__main__":
    ui = InViewUILocator()

    print("\n=== FIXED BUTTON EXAMPLES ===")
    print("Start:", ui.get_inview_button("start"))
    print("Continue:", ui.get_inview_button("Continue"))
    print("Review Export CSV:", ui.get_review_button("Sample_Export_csv"))
    print("EH target load:", ui.get_method_field("eh", "target load"))


    print("\n=== OPEN DIALOG ===")
    try:
        print(ui.find_open_dialog_controls())
    except Exception as e:
        print("Open dialog not available:", e)

    print("\n=== Save DIALOG ===")
    try:
        print(ui.find_save_dialog_controls())
    except Exception as e:
        print("save dialog not available:", e)


    print("\n=== RELATIVE MOVE ===")
    try:
        rel = ui.find_relative_move_controls()
        print(rel)
        if rel and rel["widget_box"]:
            print("Right arrow point:", ui.get_relative_move_arrow_position("right"))
    except Exception as e:
        print("Relative Move not available:", e)

    print("\n=== INDENT ARRAY ===")
    try:
        print(ui.find_indent_array_controls())
    except Exception as e:
        print("Indent array dialog not available:", e)

    print("\n=== INVIEW MAIN STATE ===")
    try:
        ui.print_main_state()
    except Exception as e:
        print("Could not read main state:", e)