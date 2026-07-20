from pathlib import Path
import requests

class InstrumentClient:
    def __init__(self, host, port=5000, token="CHANGE_THIS", timeout=300):
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"X-API-Token": token})

    def ping(self):
        r = self.session.get(f"{self.base_url}/ping", timeout=30)
        r.raise_for_status()
        return r.json()

    def call_auto(self, method, *args, **kwargs):
        payload = {
            "method": method,
            "args": list(args),
            "kwargs": kwargs,
        }
        r = self.session.post(
            f"{self.base_url}/call_auto",
            json=payload,
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()
    
    # def automate_alignment_area1(self):
    #     r = self.session.post(
    #         f"{self.base_url}/automate_alignment_area1",
    #         timeout=self.timeout,
    #     )
    #     r.raise_for_status()
    #     return r.json()

    def automate_alignment_area1(
        self,
        macro_image_path,
        macro_scale_x=0.1556,
        macro_scale_y=0.1556,
        area_name="Area1",
    ):
        macro_image_path = Path(macro_image_path)

        with open(macro_image_path, "rb") as f:
            files = {
                "macro_image": (macro_image_path.name, f, "image/png")
            }
            data = {
                "macro_scale_x": str(macro_scale_x),
                "macro_scale_y": str(macro_scale_y),
                "area_name": area_name,
            }

            r = self.session.post(
                f"{self.base_url}/automate_alignment_area1",
                files=files,
                data=data,
                timeout=self.timeout,
            )

        r.raise_for_status()
        return r.json()

    def download_last_export(self, local_dir="."):
        r_info = self.session.get(f"{self.base_url}/last_export", timeout=30)
        r_info.raise_for_status()
        info = r_info.json()

        filename = info["name"]
        local_dir = Path(local_dir)
        local_dir.mkdir(parents=True, exist_ok=True)
        local_path = local_dir / filename

        r = self.session.get(
            f"{self.base_url}/download_last_export",
            stream=True,
            timeout=self.timeout,
        )
        r.raise_for_status()

        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return {"status": "ok", "local_path": str(local_path), "filename": filename}

    def download_file(self, directory, filename, local_dir="."):
        payload = {"directory": directory, "filename": filename}
        r = self.session.post(
            f"{self.base_url}/download_file",
            json=payload,
            stream=True,
            timeout=self.timeout,
        )
        r.raise_for_status()

        local_dir = Path(local_dir)
        local_dir.mkdir(parents=True, exist_ok=True)
        local_path = local_dir / filename

        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return {"status": "ok", "local_path": str(local_path), "filename": filename}
    

    def restore_alignment(
        self,
        area_name,
        new_origin_macro,
        new_origin_micro,
        macro_scale_x,
        macro_scale_y,
        macro_image_path=None,
    ):
        payload = {
            "area_name": area_name,
            "new_origin_macro": list(new_origin_macro),
            "new_origin_micro": list(new_origin_micro),
            "macro_scale_x": float(macro_scale_x),
            "macro_scale_y": float(macro_scale_y),
            "macro_image_path": macro_image_path,
        }

        r = self.session.post(
            f"{self.base_url}/restore_alignment",
            json=payload,
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

        
    def move_to_aligned_point(self, area_name, x, y, plane_params=None):
        payload = {
            "area_name": area_name,
            "x": float(x),
            "y": float(y),
            "plane_params": plane_params,
        }

        r = self.session.post(
            f"{self.base_url}/move_to_aligned_point",
            json=payload,
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    
    def move_to_aligned_point_abs(self, area_name, x, y, plane_params=None):
        payload = {
            "area_name": area_name,
            "x": float(x),
            "y": float(y),
            "plane_params": plane_params,
        }

        r = self.session.post(
            f"{self.base_url}/move_to_aligned_point_abs",
            json=payload,
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()