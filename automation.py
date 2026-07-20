import os
import pyautogui
import time
import pandas as pd
import pytesseract
import numpy as np
# from button_locator import ButtonLocator
# from screen_utils import ScreenUtils
import random
import string
import cv2
import re
# from image_processing import ImageProcessing
import math


# New ones
import ctypes
from pywinauto import Desktop
from enforce_windows import enforce_window_function
# from ui_locator import get_method_parameter_positions


from ui_locator import InViewUILocator



class Automation:
    def __init__(self, image_directory="assets"):
        self.image_directory = image_directory
        self.default_directory = r"C:\Users\vchawla\OneDrive\Automation Tests\Trial 1"
        self.default_file_name = "_Results.csv"
        self.default_file_path = os.path.join(self.default_directory, self.default_file_name)

        # WinAPI mouse
        self.user32 = ctypes.windll.user32

        # UI locator
        self.ui = InViewUILocator(
            inview_title="InView RunTest-inForce1000",
            review_title_contains="InView ReviewData",
            open_dialog_title="Open",
            indent_array_title="Generate Indent Array",
            Save_As = "Save As",
        )

        # Fixed button offsets
        self.fixed_offsets = self.ui.OFFSET_INVIEW
        self.review_fixed_offsets = self.ui.OFFSET_REVIEW

        self.default_window_title = self.ui.inview_title
    

    


    # def stop_tests_on_indenter(self, t=1, all_tests=1, on_indenter=1):
    #     """
    #     Automates the process of stopping tests.
    #     """

    #     stop_X, stop_Y = self.locator.get_button_coordinates('stop')
    #     pyautogui.click(stop_X, stop_Y)
    #     time.sleep(t)

    #     if all_tests == 1:
    #         stop_yes_X, stop_yes_Y = self.locator.get_button_coordinates('stop_yes')
    #         pyautogui.click(stop_yes_X, stop_yes_Y)
    #         time.sleep(t)
    #     else:
    #         stop_no_X, stop_no_Y = self.locator.get_button_coordinates('stop_no')
    #         pyautogui.click(stop_no_X, stop_no_Y)
    #         time.sleep(t)

    #     if on_indenter==1:
    #         abort_X, abort_Y = self.locator.get_button_coordinates('abort')
    #         pyautogui.click(abort_X, abort_Y)
    #         time.sleep(t)       

        





    def starting_tests(
        self,
        sample_name,
        t=2,
        setup=None,
        indents=None,
        remove_n=0,
        method_type="eh",
        use_import=0,
        import_dir=None,
        import_file_name=None,
    ):
        """
        Automates the process of setting up tests.

        Parameters
        ----------
        sample_name : str
            Sample name to create.
        t : float
            Base sleep time.
        setup : dict or None
            Method parameter values.
        indents : dict or None
            Indent-array values for manual array entry mode.
        remove_n : int
            Number of existing entries to remove before adding new one.
        method_type : str
            Method parameter map type.
        use_import : int
            If 1, import indent array from file after opening Generate Indent Array.
            If 0, use normal/manual indent array flow.
        import_dir : str or None
            Directory containing the import file.
        import_file_name : str or None
            File name to import.
        """

        for i in range(int(remove_n)):
            try:
                self.click_fixed_button("remove", window_title="InView RunTest-inForce1000")
                time.sleep(t)
            except Exception as e:
                print(f"[remove_items] 'remove' button failed on iteration {i+1}. Stopping. Error: {e}")
                break

        # Sample setup
        self.click_fixed_button("Test_name_loc", window_title="InView RunTest-inForce1000")
        time.sleep(t)

        self.click_fixed_button("Add", window_title="InView RunTest-inForce1000")
        time.sleep(t)

        self.click_fixed_button("Sample_name", window_title="InView RunTest-inForce1000")
        time.sleep(t)

        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")
        time.sleep(0.1)

        pyautogui.write(sample_name, interval=0.05)
        time.sleep(0.1)

        self.click_fixed_button("Continue", window_title="InView RunTest-inForce1000")
        time.sleep(t)

        if setup is None:
            self.click_fixed_button("Continue", window_title="InView RunTest-inForce1000")
            time.sleep(t)
        else:
            self.apply_method_parameters_ui(
                setup=setup,
                method_type=method_type,
                window_title="InView RunTest-inForce1000",
                t=max(2, t/3)
            )

            self.click_fixed_button("Continue", window_title="InView RunTest-inForce1000")
            time.sleep(t)

        # Generate Indent Array
        self.click_fixed_button("clear all", window_title="InView RunTest-inForce1000")
        time.sleep(t)

        self.click_fixed_button("array", window_title="InView RunTest-inForce1000")
        time.sleep(t)

        # --------------------------------------------------
        # IMPORT MODE
        # --------------------------------------------------
        if int(use_import) == 1:
            if not import_dir:
                raise ValueError("import_dir must be provided when use_import=1")
            if not import_file_name:
                raise ValueError("import_file_name must be provided when use_import=1")

            # Find controls in Generate Indent Array
            indent_controls = self.ui.find_indent_array_controls()

            import_ctrl = indent_controls.get("Import")
            if import_ctrl is None:
                import_ctrl = indent_controls.get("import")

            if import_ctrl is None:
                raise RuntimeError("Import button not found in Generate Indent Array dialog")

            # Click Import in Generate Indent Array
            rect = import_ctrl["rect"]
            self.click_absolute_ui(
                rect["center_x"],
                rect["center_y"],
                window_title="Generate Indent Array",
                enforcement=0
            )
            time.sleep(1.0)

            # Open dialog and load file
            self.open_sample_from_directory(
                directory_path=import_dir,
                sample_file_name=import_file_name,
                dialog_title="Open",
            )
            time.sleep(t)



        # --------------------------------------------------
        # MANUAL ARRAY MODE
        # --------------------------------------------------
        else:
            if indents is not None:
                self.apply_indent_array_ui(indents, t=t)
            else:
                indent_controls = self.ui.find_indent_array_controls()
                ok_ctrl = indent_controls.get("OK")
                if ok_ctrl is None:
                    raise RuntimeError("OK button not found in Generate Indent Array dialog")

                rect = ok_ctrl["rect"]
                self.click_absolute_ui(
                    rect["center_x"],
                    rect["center_y"],
                    window_title="Generate Indent Array",
                    enforcement=0
                )
                time.sleep(t)

        # Final continue
        self.click_fixed_button("Continue", window_title="InView RunTest-inForce1000")
        time.sleep(t)
        
    def start_test_normal(self, t=2):
        self.click_fixed_button("start", window_title="InView RunTest-inForce1000")    
        time.sleep(t)
    

    def move(self, amount, direction, t=2, tt=4, time_trial=None, Backlash=None):
        """
        Automates the movement process by entering a number and clicking direction buttons.
        """
        
        # Right-click to open the context menu
        self.right_click_fixed_button("right click location", window_title="InView RunTest-inForce1000")
        time.sleep(0.5)

        # Right-click on "move_relative"
        self.click_fixed_button("move relative", window_title="InView RunTest-inForce1000") 



        # Step 1: find Relative Move controls from UI
        rel = self.ui.find_relative_move_controls()
        if rel is None or rel.get("edit") is None:
            raise RuntimeError("Relative Move input field not found")

        # Step 2: click number/edit field
        edit_rect = rel["edit"]["rect"]
        self.click_absolute_ui(
            edit_rect["center_x"],
            edit_rect["center_y"],
            window_title="InView RunTest-inForce1000",
            enforcement=0
        )
        time.sleep(t)

        # Step 3: clear and type amount
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")
        time.sleep(t)
        pyautogui.write(str(amount), interval=0.1)
        time.sleep(t)

        # Step 4: click direction arrow from UI locator
        direction_buttons = ["right", "left", "up", "down"]

        if direction in direction_buttons:
            x, y = self.ui.get_relative_move_arrow_position(direction)
            self.click_absolute_ui(
                x,
                y,
                window_title="InView RunTest-inForce1000",
                enforcement=0
            )
        else:
            print("Invalid direction specified. Please use 'right', 'left', 'up', or 'down'.")
            return

        time.sleep(tt)



        # Step 4: Perform backlash correction
        if Backlash is None:
            # Right-click to open the context menu
            self.right_click_fixed_button("right click location", window_title="InView RunTest-inForce1000")
            time.sleep(1)
            self.click_fixed_button("remove backlash", window_title="InView RunTest-inForce1000") 
            time.sleep(1)

        
    def move_in_increments(self, total_amount, direction, increment, t=2, tt=4, time_trial=None, Backlash=None):
        """
        Automates the movement process in increments. Moves the specified amount in the given direction using defined increments.
        
        Args:
            total_amount (int): The total distance to move.
            direction (str): The direction to move ('right', 'left', 'up', 'down').
            increment (int): The step size for each movement.
            t (int, optional): Time delay after each step. Default is 2.
            tt (int, optional): Time delay after each full step cycle. Default is 4.
            time_trial (optional): Additional parameter for future use. Default is None.
            Backlash (optional): Specifies if backlash correction should be applied. Default is None.
        """
        remaining_amount = total_amount
        
        while remaining_amount > 0:
            step_amount = min(remaining_amount, increment)
            print(f"Moving {step_amount} in direction {direction}")
            
            # Call the move method with the step amount
            self.move(step_amount, direction, t=t, tt=tt, time_trial=time_trial, Backlash=Backlash)
            
            # Subtract the step amount from the remaining amount
            remaining_amount -= step_amount
            time.sleep(1)  # Small delay between steps for stability

        print(f"Movement of {total_amount} in {direction} direction completed in increments of {increment}.")
    
######################################################################################################################
    def process_review_file(
        self,
        sample_names,
        open_dir=None,
        current_sample_file_name=None,
        export_dir=None,
        export_file_name=None,
        review_changes=None,
        review_type="eh",
        export_format="excel",
        load_wait=30,
        recalc_wait=30,
        save_wait=5,
    ):
        # Step 1: find initial ReviewData window more flexibly
        dlg, review_title, matched_sample = self._get_initial_review_title_info(
            sample_names=sample_names,
            prefer_shortest=True,
        )
        print(f"[REVIEW] Initial window: {review_title}")
        print(f"[REVIEW] Initial matched sample: {matched_sample}")

        # Step 2: get file into review window
        if open_dir is None:
            before_snapshot = self.get_window_text_snapshot(review_title)

            self.click_review_button("New Data Available", window_title=review_title)

            self.wait_until_review_changes(
                window_title=review_title,
                before_snapshot=before_snapshot,
                timeout=load_wait,
                poll=0.5,
            )
        else:
            old_review_title = review_title

            self.click_review_button("Sample File", window_title=review_title)
            time.sleep(0.5)

            self.click_review_button("Open Sample", window_title=review_title)
            time.sleep(1.0)

            file_name_to_open = current_sample_file_name or matched_sample
            self.open_sample_from_directory(open_dir, file_name_to_open)
            time.sleep(load_wait)

            review_title = self.wait_for_review_title_update(
                old_title=old_review_title,
                timeout=10,
                poll=0.5,
            )
            print(f"[REVIEW] Title after open: {review_title}")
        
            while self.window_exists("Please wait.", match="exact"):
                print(" Waiting")
                time.sleep(5)

        # Step 3: optional recalculation parameter edits
        if review_changes:
            self.apply_review_parameters_ui(
                review_changes=review_changes,
                review_type=review_type,
                window_title=review_title,
                t=0.2,
            )

            self.click_review_button("Sample File", window_title=review_title)
            time.sleep(0.5)

            self.click_review_button("Sample_recalculate", window_title=review_title)
            time.sleep(recalc_wait)

            while self.window_exists("Please wait.", match="exact"):
                print("Waiting for Review changes")
                time.sleep(5)
        


        # Step 4: optional Save As before export
        if export_dir is not None:
            old_review_title = review_title

            self.click_review_button("Sample File", window_title=review_title)
            time.sleep(0.5)

            self.click_review_button("Sample_Save As", window_title=review_title)
            time.sleep(1.0)

            controls = self.ui.find_saveas_dialog_controls()

            address_bar = controls.get("address_bar")
            file_name = controls.get("file_name")
            save_button = controls.get("save_button")

            if address_bar is None or file_name is None or save_button is None:
                raise RuntimeError("Save As dialog controls not found")

            rect = address_bar["rect"]
            self.click_absolute_ui(rect["center_x"], rect["center_y"], window_title="Save As", enforcement=0)
            time.sleep(0.2)
            pyautogui.hotkey("ctrl", "a")
            pyautogui.press("backspace")
            time.sleep(0.2)
            pyautogui.write(str(export_dir), interval=0.03)
            time.sleep(0.2)
            pyautogui.press("enter")
            time.sleep(1.0)

            rect = file_name["rect"]
            self.click_absolute_ui(rect["center_x"], rect["center_y"], window_title="Save As", enforcement=0)
            time.sleep(0.2)
            pyautogui.hotkey("ctrl", "a")
            pyautogui.press("backspace")
            time.sleep(0.2)

            save_name = export_file_name or matched_sample
            pyautogui.write(str(save_name), interval=0.03)
            time.sleep(0.2)

            rect = save_button["rect"]
            self.click_absolute_ui(rect["center_x"], rect["center_y"], window_title="Save As", enforcement=0)
            time.sleep(save_wait)

            review_title = self.wait_for_review_title_update(
                old_title=old_review_title,
                timeout=10,
                poll=0.5,
            )
            print(f"[REVIEW] Title after Save As: {review_title}")

            while self.window_exists("Save As", match="exact"):
                print("Save As window error")
                time.sleep(5)

        # Step 5: export
        self.click_review_button("Sample File", window_title=review_title)
        time.sleep(0.5)

        self.click_review_button("Sample_Export", window_title=review_title)
        time.sleep(0.5)

        export_format = str(export_format).strip().lower()
        if export_format == "csv":
            self.click_review_button("Sample_Export_csv", window_title=review_title)
        else:
            self.click_review_button("Sample_Export_excel", window_title=review_title)

        return {
            "review_title": review_title,
            "matched_sample": matched_sample,
            "open_dir": open_dir,
            "export_dir": export_dir,
            "export_format": export_format,
        }



    def get_xyz_positions(self):
        """
        Return only:
            (x_axis_position, y_axis_position, extension)

        Uses ui.read_main_state() instead of OCR.
        Missing values come back as float('nan').
        """
        state = self.ui.read_main_state()

        x_val = self._metric_value_or_nan(state, "X Axis Position")
        y_val = self._metric_value_or_nan(state, "Y Axis Position")
        extension_val = self._metric_value_or_nan(state, "Extension")

        return x_val, y_val, extension_val


    
    def get_all_ui_state(self):
        """
        Return all available UI state values as a flat dictionary:
            {
                "Extension": ...,
                "Force": ...,
                "Displacement": ...,
                ...
            }

        Values are numeric when available, otherwise float('nan').
        """
        raw_state = self.ui.read_main_state()

        result = {}
        for key in raw_state:
            result[key] = self._metric_value_or_nan(raw_state, key)

        return result



    def set_extension(self, number, t=2):
        """
        Sets the extension value through the automation workflow.
        """
        if number <= 11.01:

            # Right-click on "move_relative"
            self.click_fixed_button("Z_control", window_title="InView RunTest-inForce1000") 
            time.sleep(t)
            OriginX_small, OriginY_small, Extension_origin = self.get_xyz_positions()

            if number > Extension_origin:
                self.click_fixed_button("Displacement in Z", window_title="InView RunTest-inForce1000")
                time.sleep(t)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                time.sleep(t)
                pyautogui.write(str(12.5), interval=0.1)
                time.sleep(t)

                self.click_fixed_button("Displacement in Z set", window_title="InView RunTest-inForce1000")
                time.sleep(t)

                self.click_fixed_button("Engage in Z", window_title="InView RunTest-inForce1000")
                time.sleep(t)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                time.sleep(t)
                pyautogui.write(str(number), interval=0.1)
                self.click_fixed_button("Engage in Z set", window_title="InView RunTest-inForce1000")
                time.sleep(5)

                # print("here")
                val = self.window_exists("Control panel set extension", match="contains" )
                print("popup check =", val)
                while self.window_exists("Control panel set extension", match="contains"):
                    print("Waiting for Extension")
                    time.sleep(5)

                self.click_fixed_button("Engage in Z", window_title="InView RunTest-inForce1000")
                time.sleep(t)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                time.sleep(t)
                pyautogui.write("0.00", interval=0.1)
                pyautogui.press("enter")
                time.sleep(t)               


                self.click_fixed_button("Displacement in Z", window_title="InView RunTest-inForce1000")
                time.sleep(t)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                time.sleep(t)
                pyautogui.write(str(0.0), interval=0.1)
                time.sleep(t)
            else:
                # self.click_fixed_button("Engage in Z", window_title="InView RunTest-inForce1000")
                # time.sleep(t)
                # pyautogui.hotkey('ctrl', 'a')
                # pyautogui.press('backspace')
                # time.sleep(t)
                # pyautogui.write(str(number), interval=0.1)
                # self.click_fixed_button("Engage in Z set", window_title="InView RunTest-inForce1000")
                # time.sleep(5)

                # val = self.window_exists("Control panel set extension" , match="contains")
                # print("popup check =", val)

                # while self.window_exists("Control panel set extension", match="contains"):
                #     print("Waiting for Extension")
                #     time.sleep(5)
                

                # self.click_fixed_button("Engage in Z", window_title="InView RunTest-inForce1000")
                # time.sleep(t)
                # pyautogui.hotkey('ctrl', 'a')
                # pyautogui.press('backspace')
                # time.sleep(t)
                # pyautogui.write(str(0.00), interval=0.1)
                # time.sleep(t)
                self.click_fixed_button("Displacement in Z", window_title="InView RunTest-inForce1000")
                time.sleep(t)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                time.sleep(t)
                pyautogui.write(str(12.5), interval=0.1)
                time.sleep(t)

                self.click_fixed_button("Displacement in Z set", window_title="InView RunTest-inForce1000")
                time.sleep(t)

                self.click_fixed_button("Engage in Z", window_title="InView RunTest-inForce1000")
                time.sleep(t)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                time.sleep(t)
                pyautogui.write(str(number), interval=0.1)
                self.click_fixed_button("Engage in Z set", window_title="InView RunTest-inForce1000")
                time.sleep(5)

                # print("here")
                val = self.window_exists("Control panel set extension", match="contains" )
                print("popup check =", val)
                while self.window_exists("Control panel set extension", match="contains"):
                    print("Waiting for Extension")
                    time.sleep(5)

                self.click_fixed_button("Engage in Z", window_title="InView RunTest-inForce1000")
                time.sleep(t)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                time.sleep(t)
                pyautogui.write("0.00", interval=0.1)
                pyautogui.press("enter")
                time.sleep(t)               


                self.click_fixed_button("Displacement in Z", window_title="InView RunTest-inForce1000")
                time.sleep(t)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                time.sleep(t)
                pyautogui.write(str(0.0), interval=0.1)
                time.sleep(t)
        else:
            raise ValueError(f"Extension cannot be greater than 11. Given value: {number}")

    def engage(self):
        """
        Clicks the 'Engage' button on the extension control window.
        """
        self.click_fixed_button("Z_control", window_title="InView RunTest-inForce1000")
        time.sleep(2)

        self.click_fixed_button("engage", window_title="InView RunTest-inForce1000")

    def align_focus(self):
        """
        Guides the user to move to three positions and collects XYZ coordinates.
        Returns the parameters of linear interpolation for Z based on X and Y.
        """
        print("Please move to the first position and confirm to collect XYZ.")
        input("Press Enter to continue...")
        x1, y1, z1 = self.get_xyz_positions()

        print("Please move to the second position and confirm to collect XYZ.")
        input("Press Enter to continue...")
        x2, y2, z2 = self.get_xyz_positions()

        print("Please move to the third position and confirm to collect XYZ.")
        input("Press Enter to continue...")
        x3, y3, z3 = self.get_xyz_positions()

        # Perform linear interpolation to calculate plane parameters
        A = np.array([
            [x1, y1, 1],
            [x2, y2, 1],
            [x3, y3, 1]
        ])
        b = np.array([z1, z2, z3])

        plane_params = np.linalg.solve(A, b)
        print("Linear interpolation parameters (Z = ax + by + c):", plane_params)

        return plane_params  # Returns [a, b, c]

    def focus(self, plane_params):
        """
        Focuses by calculating the Z position for the given X and Y and sets the extension accordingly.
        """
        a, b, c = plane_params
        x, y, z2 = self.get_xyz_positions()
        z = round(a * x + b * y + c, 3)
        print(f"Calculated Z for X={x}, Y={y} is Z={z}")
        self.set_extension(z)

    def change_method(
        self,
        method_dir = r"C:\Program Files\Nanomechanics\MasterMethods v1.5",
        method_file_name="Advanced Dynamic E and H.NMT",
        window_title="InView RunTest-inForce1000",
        t=2,
        add=1,
    ):
        """
        Change the active method file using the Open dialog.

        Parameters:
            method_dir (str): full directory path
            method_file_name (str): exact file name (e.g. "Advanced Dynamic E and H.NMT")
        """

        # open method dialog
        self.click_fixed_button("Method File", window_title=window_title)
        time.sleep(t)

        self.click_fixed_button("Method_open", window_title=window_title)
        time.sleep(4.0)

        # reuse your existing helper (best part of your codebase)
        self.open_sample_from_directory(
            directory_path=method_dir,
            sample_file_name=method_file_name,
            dialog_title="Open",
        )

        time.sleep(5.0)

        print(f"[METHOD] Loaded: {method_file_name} from {method_dir}")

        if add==1:
            self.click_fixed_button("Method_control_settings", window_title=window_title)
            time.sleep(2.0)

            self.click_fixed_button("select_meters", window_title=window_title)
            time.sleep(2.0)

            self.click_fixed_button_no_enforcement("x_value_now", window_title="ItemSelectionListForm")
            time.sleep(2.0)

            self.click_fixed_button_no_enforcement("put_on_right", window_title="ItemSelectionListForm")
            time.sleep(2.0)

            self.click_fixed_button_no_enforcement("y_value_now", window_title="ItemSelectionListForm")
            time.sleep(2.0)

            self.click_fixed_button_no_enforcement("put_on_right", window_title="ItemSelectionListForm")
            time.sleep(2.0)

            self.click_fixed_button_no_enforcement("close_list_box", window_title="ItemSelectionListForm")
            time.sleep(1.0)

    def get_current_sample_and_test_ocr_passive(
        self,
        tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        debug=False,
    ):
        import re
        import time
        import pytesseract
        from PIL import ImageGrab

        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        # no clicks, no enforce_window_function
        img = ImageGrab.grab()
        text = pytesseract.image_to_string(img)

        if debug:
            print("----- OCR TEXT -----")
            print(text[:2000])

        test_number = None
        m = re.search(r"Tests\s*:\s*(\d+)", text, flags=re.IGNORECASE)
        if m:
            test_number = int(m.group(1))

        return {
            "test_number": test_number,
            "raw_text": text,
        }

    def get_current_sample_and_test_ocr(
        self,
        tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        window_title="InView RunTest-inForce1000",
        debug=False,
    ):
        """
        OCR the InView screen and extract:
            - sample name (if found)
            - current test number from 'Tests: N'

        Returns
        -------
        dict
            {
                "sample_name": str or None,
                "test_number": int or None,
                "raw_text": str
            }
        """
        import re
        import pytesseract
        from PIL import ImageGrab

        enforce_window_function(WINDOW_TITLE=window_title)
        time.sleep(0.5)

        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        img = ImageGrab.grab()
        text = pytesseract.image_to_string(img)

        if debug:
            print("----- OCR TEXT -----")
            print(text[:2000])

        sample_name = None
        test_number = None

        # -----------------------------
        # Find test number from "Tests: N"
        # -----------------------------
        m_test = re.search(r"Tests\s*:\s*(\d+)", text, flags=re.IGNORECASE)
        if m_test:
            try:
                test_number = int(m_test.group(1))
            except Exception:
                test_number = None

        # -----------------------------
        # Try to find sample name
        # Cases:
        #   "Method: ... Sample: Tests"
        #   "PROJECT NAME"
        #   next line contains actual sample/project name
        # -----------------------------
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        # First try: direct "Sample: xxx"
        m_sample = re.search(r"Sample\s*:\s*(.+?)(?:\s+Tests\s*:|\s*$)", text, flags=re.IGNORECASE)
        if m_sample:
            candidate = m_sample.group(1).strip()
            if candidate:
                sample_name = candidate

        # Second try: look after PROJECT NAME
        if not sample_name:
            for i, line in enumerate(lines):
                if line.strip().lower() == "project name":
                    if i + 1 < len(lines):
                        candidate = lines[i + 1].strip()
                        if candidate:
                            sample_name = candidate
                            break

        # Clean obvious junk
        if sample_name:
            sample_name = re.sub(r"\s+", " ", sample_name).strip()

        return {
            "sample_name": sample_name,
            "test_number": test_number,
            "raw_text": text,
        }    

    
    def capture_video_panel(
        self,
        panel_rect=(232, 134, 1419, 1037),
        window_title="InView RunTest-inForce1000",
        save_path=None,
        plot=True,
        as_numpy=True,
    ):
        """
        Capture the Video Panel region.

        Parameters
        ----------
        panel_rect : tuple
            (left, top, right, bottom) screen coordinates
        window_title : str
            InView window title to bring forward first
        save_path : str or None
            If provided, save image there
        plot : bool
            If True, display the captured image
        as_numpy : bool
            If True, also return numpy array

        Returns
        -------
        dict
            {
                "pil_image": PIL.Image,
                "np_image": np.ndarray or None,
                "rect": panel_rect,
                "save_path": save_path
            }
        """
        import numpy as np
        import matplotlib.pyplot as plt
        from PIL import ImageGrab

        

        enforce_window_function(WINDOW_TITLE=window_title)
        time.sleep(0.5)

        left, top, right, bottom = panel_rect
        img = ImageGrab.grab(bbox=(left, top, right, bottom))

        if save_path is not None:
            img.save(save_path)

        np_img = np.array(img) if as_numpy else None

        if plot:
            plt.figure(figsize=(8, 6))
            plt.imshow(img)
            plt.title("Captured Video Panel")
            plt.axis("off")
            plt.show()

        return {
            "pil_image": img,
            "np_image": np_img,
            "rect": panel_rect,
            "save_path": save_path,
        }
    
    def capture_video_panel_remote(
        self,
        panel_rect=(232, 134, 1419, 1037),
        window_title="InView RunTest-inForce1000",
        save_path=r"C:\Users\Public\Documents\Nanomechanics\Profiles\Shared AENI\remote_video_panel.png",
    ):
        
        self.capture_video_panel(
            panel_rect=panel_rect,
            window_title=window_title,
            save_path=save_path,
            plot=False,
            as_numpy=False,
        )

        return {
            "status": "ok",
            "save_path": str(save_path),
        }
    
    def align_focus_remote(self):
        plane_params = self.align_focus()
        return [float(x) for x in plane_params]



    
        
    def start_single_Normal_tests(self, name=None, length=8):
        if name is None:            
            # Generate a random name
            random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
            name=random_name
        # Engage
        self.engage()
        while True:
             time.sleep(10)
             center_coords = self.locator.get_button_coordinates("abort")
             
             if not center_coords:
                   print(f"Image 'abort' not found. Rechecking in 10 seconds...")
                   time.sleep(10)
                   center_coords_second_check = self.locator.get_button_coordinates("abort")
                   if not center_coords_second_check:
                         print(f"Image 'abort' confirmed as not present. Waiting for 30 more seconds...")
                         time.sleep(30)
                         break
                   else:
                          print("Second check failed. Restarting wait loop...")
             else:
                   print("Image 'abort' found. Still waiting for it to disappear...")
                   
        # Click the "start" button
        start_X, start_Y = self.locator.get_button_coordinates("start")
        pyautogui.click(start_X, start_Y)
        time.sleep(2)
        
		# Find edges of the image
        image_name='file name'
        window_image_path = f"{self.image_directory}/{image_name}.png"
        edges = ScreenUtils.find_image_edges_on_screen(window_image_path, monitor_index=2, threshold=0.8)
        top_left_x, top_left_y, bottom_right_x, bottom_right_y = edges

        # Click at the rightmost and center Y
        click_x = bottom_right_x
        click_y = (top_left_y + bottom_right_y) // 2
        pyautogui.click(click_x, click_y)
        time.sleep(2)

        # Enter the random name
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(2)
        pyautogui.write(name, interval=0.1)
        time.sleep(2)
        
        save_X, save_Y = self.locator.get_button_coordinates("save")  
        pyautogui.click(save_X, save_Y)
		# Now the test is started
        
        while True:
            time.sleep(10)
            center_coords = self.locator.get_button_coordinates('start')
            if center_coords:
                print(f"Image start found at {center_coords}. Waiting for 1 more minute...")
                time.sleep(60)
                break
            else:
                print(f"Image start not found. Still waiting...")
                time.sleep(60) 
                
        # Set extension to 10
        self.set_extension(10, t=2)



    

    ###################################################################################
    # UI based default methods
    def get_fixed_button_abs_coords_no_enforcement(
        self,
        button_name,
        window_title=None,
        review_sample_name=None,
    ):
        """
        Return absolute screen coordinates for a fixed-offset button
        without enforcing/resizing/repositioning the window.
        """
        if button_name not in self.fixed_offsets:
            raise ValueError(
                f"Fixed button '{button_name}' not found in self.fixed_offsets."
            )

        title = self._resolve_window_title(
            window_title=window_title,
            review_sample_name=review_sample_name,
        )

        from pywinauto import Desktop

        desktop = Desktop(backend="win32")
        dlg = desktop.window(title=title)
        dlg.wait("visible", timeout=10)

        try:
            dlg.set_focus()
        except Exception:
            pass

        client = dlg.client_rect()

        x_rel, y_rel = self.fixed_offsets[button_name]
        x = client.left + x_rel
        y = client.top + y_rel

        return int(x), int(y), title

    
    def click_fixed_button_no_enforcement(
        self,
        button_name,
        window_title=None,
        review_sample_name=None,
        pause=0.1,
    ):
        """
        Click a fixed-offset button without enforcing window size/position.
        """
        x, y, title = self.get_fixed_button_abs_coords_no_enforcement(
            button_name,
            window_title=window_title,
            review_sample_name=review_sample_name,
        )

        self.click_absolute_ui(
            x,
            y,
            window_title=title,
            pause=pause,
            enforcement=0,
        )
        
    def set_cursor(self, x, y):
        self.user32.SetCursorPos(int(x), int(y))

    def left_click(self):
        self.user32.mouse_event(2, 0, 0, 0, 0)  # left down
        self.user32.mouse_event(4, 0, 0, 0, 0)  # left up
    
    def right_click(self):
        self.user32.mouse_event(8, 0, 0, 0, 0)   # right down
        self.user32.mouse_event(16, 0, 0, 0, 0)  # right up

    def _resolve_window_title(self, window_title=None, review_sample_name=None):
        if window_title is not None:
            return window_title
        if review_sample_name is not None:
            return f"InView ReviewData - {review_sample_name}"
        return self.default_window_title

    def _get_window_client_rect(self, window_title=None, review_sample_name=None):
        title = self._resolve_window_title(
            window_title=window_title,
            review_sample_name=review_sample_name
        )

        enforce_window_function(WINDOW_TITLE=title)

        desktop = Desktop(backend="win32")
        dlg = desktop.window(title=title)
        dlg.wait("visible", timeout=10)
        dlg.set_focus()

        client = dlg.client_rect()
        return dlg, client, title

    def get_fixed_button_abs_coords(self, button_name, window_title=None, review_sample_name=None):
        if button_name not in self.fixed_offsets:
            raise ValueError(
                f"Fixed button '{button_name}' not found in self.fixed_offsets. "
                f"Add it from your ui locator first."
            )

        _, client, title = self._get_window_client_rect(
            window_title=window_title,
            review_sample_name=review_sample_name
        )

        x_rel, y_rel = self.fixed_offsets[button_name]
        x = client.left + x_rel
        y = client.top + y_rel

        return int(x), int(y), title

    def click_fixed_button(self, button_name, window_title=None, review_sample_name=None, pause=0.1):
        x, y, title = self.get_fixed_button_abs_coords(
            button_name,
            window_title=window_title,
            review_sample_name=review_sample_name
        )

        print(f"[FIXED CLICK] {button_name} @ ({x}, {y}) in '{title}'")
        self.set_cursor(x, y)
        time.sleep(pause)
        self.left_click()

    def right_click_fixed_button(self, button_name, window_title=None, review_sample_name=None, pause=0.1):
        x, y, title = self.get_fixed_button_abs_coords(
            button_name,
            window_title=window_title,
            review_sample_name=review_sample_name
        )

        print(f"[FIXED RIGHT CLICK] {button_name} @ ({x}, {y}) in '{title}'")

        self.set_cursor(x, y)
        time.sleep(pause)
        self.right_click()

    def hover_fixed_button(self, button_name, window_title=None, review_sample_name=None, pause=1.0):
        x, y, title = self.get_fixed_button_abs_coords(
            button_name,
            window_title=window_title,
            review_sample_name=review_sample_name
        )

        print(f"[FIXED HOVER] {button_name} @ ({x}, {y}) in '{title}'")
        self.set_cursor(x, y)
        time.sleep(pause)

        
    def _get_method_param_map(self, method_type):
        method_type = method_type.strip().lower()

        if method_type in ["eh", "in_view_eh", "eh_method"]:
            return self.ui.IN_VIEW_EH_METHOD

        elif method_type in ["constant_disp", "constant displacement", "in_view_constant_disp"]:
            return self.ui.IN_VIEW_CONSTANT_DISP_METHOD

        else:
            raise ValueError(f"Unsupported method_type: {method_type}")
        
    def click_absolute_ui(self, x, y, window_title="InView RunTest-inForce1000", pause=0.1, enforcement=1):
        if enforcement==1:
            enforce_window_function(WINDOW_TITLE=window_title)
        self.set_cursor(x, y)
        time.sleep(pause)
        self.left_click()

    def clear_and_type_at_ui(self, x, y, text, window_title="InView RunTest-inForce1000", t=0.2):
        self.click_absolute_ui(x, y, window_title=window_title)
        time.sleep(t)

        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")
        time.sleep(t)

        pyautogui.write(str(text), interval=0.05)
        time.sleep(t)

    def apply_method_parameters_ui(self, setup, method_type, window_title="InView RunTest-inForce1000", t=0.2):
        """
        setup: dict of parameter_name -> value
        method_type: 'eh' or 'constant_disp'
        Only provided parameters are changed. Missing ones are left untouched.
        """
        if setup is None:
            return

        pos_map = self._get_method_param_map(method_type)

        def _fmt(v):
            try:
                fv = float(v)
                if math.isfinite(fv):
                    return f"{fv:g}"
            except Exception:
                pass
            return str(v)

        for raw_name, val in setup.items():
            if val is None:
                continue

            name = raw_name.strip().lower()

            if isinstance(val, str) and val.strip() == "-1":
                continue
            if val == -1:
                continue

            if name not in pos_map:
                print(f"[apply_method_parameters_ui] Warning: '{raw_name}' not found for method '{method_type}'. Skipping.")
                continue

            x, y = pos_map[name]

            if name in ["drift", "metal"]:
                text = "1" if bool(val) else "0"
            else:
                text = _fmt(val)

            self.clear_and_type_at_ui(
                x, y, text,
                window_title=window_title,
                t=max(0.1, t)
            )

        pyautogui.press("enter")
        time.sleep(t)


    def apply_indent_array_ui(self, indents, t=0.2):
        indent_controls = self.ui.find_indent_array_controls()

        def _fmt_indent(v):
            try:
                return str(int(round(float(v))))
            except Exception:
                return str(v)

        def _fmt_spacing(v):
            try:
                fv = float(v)
                return f"{fv:g}" if math.isfinite(fv) else str(v)
            except Exception:
                return str(v)

        for name, val in indents.items():
            if val is None:
                continue
            if val == -1:
                continue
            if isinstance(val, str) and val.strip() == "-1":
                continue

            ctrl = indent_controls.get(name)
            if ctrl is None:
                print(f"[indents] Warning: '{name}' control not found; skipping.")
                continue

            rect = ctrl["rect"]
            self.click_absolute_ui(
                rect["center_x"],
                rect["center_y"],
                window_title="Generate Indent Array",
                enforcement=0
            )
            time.sleep(0.25)

            pyautogui.hotkey("ctrl", "a")
            pyautogui.press("backspace")
            time.sleep(0.15)

            if "indents" in name.lower():
                text = _fmt_indent(val)
            else:
                text = _fmt_spacing(val)

            pyautogui.write(text, interval=0.05)
            time.sleep(0.15)

        pyautogui.press("enter")

        ok_ctrl = indent_controls.get("OK")
        if ok_ctrl is None:
            raise RuntimeError("OK button not found in Generate Indent Array dialog")

        rect = ok_ctrl["rect"]
        self.click_absolute_ui(
            rect["center_x"],
            rect["center_y"],
            window_title="Generate Indent Array",
            enforcement=0
        )
        time.sleep(t)


    def _metric_value_or_nan(self, state, key):
        """
        Return numeric value from ui.read_main_state().
        If missing/nan/unavailable, return float('nan').
        """
        item = state.get(key)
        if not item:
            return float("nan")

        status = item.get("status")
        if status == "ok" or status == "nan":
            val = item.get("value")
            try:
                return float(val)
            except Exception:
                return float("nan")

        return float("nan")

    from pywinauto import Desktop


    def window_exists(
        self,
        window_name: str,
        match="contains",   # "contains", "exact", "startswith", "regex"
        visible_only=True,
    ):
        """
        Robust window detection.

        Parameters:
            window_name (str): text to match
            match (str): matching mode
            visible_only (bool): ignore hidden/ghost windows

        Returns:
            bool
        """
        from pywinauto import Desktop
        import re

        target = window_name.strip().lower()
        desktop = Desktop(backend="win32")

        for w in desktop.windows():
            try:
                title = w.window_text()
                if not title:
                    continue

                title_clean = title.strip().lower()

                # --- matching modes ---
                if match == "exact":
                    ok = (title_clean == target)

                elif match == "startswith":
                    ok = title_clean.startswith(target)

                elif match == "regex":
                    ok = re.search(target, title_clean) is not None

                else:  # default = contains
                    ok = (target in title_clean)

                if not ok:
                    continue

                wrapper = desktop.window(handle=w.handle)

                if not wrapper.exists():
                    continue

                if visible_only and not wrapper.is_visible():
                    continue

                return True

            except Exception:
                pass

        return False
    ###################################################################################
    # Review Helopers

    def _as_sample_list(self, sample_names):
        if isinstance(sample_names, str):
            return [sample_names]
        return [str(x) for x in sample_names]

    def _review_window_title(self, sample_name):
        return f"InView ReviewData - {sample_name.strip()}"

    def _find_existing_review_title(self, sample_names):
        candidates = self._as_sample_list(sample_names)

        for name in candidates:
            title = self._review_window_title(name)
            try:
                dlg = self.ui.desktop.window(title=title)
                dlg.wait("exists", timeout=1)
                dlg.wait("visible", timeout=1)
                return title, name
            except Exception:
                pass

        raise RuntimeError(
            f"No matching ReviewData window found for samples: {candidates}"
        )
    

    def apply_review_parameters_ui(self, review_changes, review_type="eh", sample_name=None, window_title=None, t=0.2):
        if review_changes is None:
            return

        if window_title is None:
            if sample_name is None:
                raise ValueError("Either sample_name or window_title must be provided")
            window_title = self._review_window_title(sample_name)

        def _fmt(v):
            try:
                fv = float(v)
                if math.isfinite(fv):
                    return f"{fv:g}"
            except Exception:
                pass
            return str(v)

        dlg = self._get_review_dialog(
            window_title=window_title,
            sample_names=[sample_name] if sample_name is not None else None,
        )

        try:
            dlg.set_focus()
        except Exception:
            pass

        client = dlg.client_rect()
        actual_title = dlg.window_text()

        for raw_name, val in review_changes.items():
            if val is None:
                continue
            if val == -1:
                continue
            if isinstance(val, str) and val.strip() == "-1":
                continue

            try:
                x_rel, y_rel = self.ui.get_review_parameter(review_type, raw_name)
            except Exception as e:
                print(f"[review params] Warning: '{raw_name}' not found for review_type='{review_type}'. Skipping. Error: {e}")
                continue

            x = client.left + x_rel
            y = client.top + y_rel

            print(f"[REVIEW PARAM] {raw_name} -> {val} @ ({x}, {y}) in '{actual_title}'")

            self.click_absolute_ui(x, y, window_title=actual_title, enforcement=0)
            time.sleep(t)

            pyautogui.hotkey("ctrl", "a")
            pyautogui.press("backspace")
            time.sleep(t)

            pyautogui.write(_fmt(val), interval=0.04)
            time.sleep(t)

            pyautogui.press("enter")
            time.sleep(t)   


    def _get_initial_review_dialog(self, sample_names=None, prefer_shortest=True):
        """
        Find the initial ReviewData dialog to start from.

        Strategy:
        1. collect all visible ReviewData windows
        2. if sample_names provided, prefer titles containing one of them
        3. otherwise choose the shortest title if prefer_shortest=True
        4. otherwise choose the last visible one
        """
        windows = []

        for w in self.ui.desktop.windows():
            try:
                txt = w.window_text().strip()
                if not txt:
                    continue
                if "InView ReviewData" not in txt:
                    continue

                wrapper = self.ui.desktop.window(handle=w.handle)
                if wrapper.exists() and wrapper.is_visible():
                    windows.append(wrapper)
            except Exception:
                pass

        if not windows:
            raise RuntimeError("No visible ReviewData window found")

        # Prefer active one first
        for dlg in windows:
            try:
                if dlg.has_focus():
                    return dlg
            except Exception:
                pass

        # Prefer any title matching sample names
        if sample_names:
            sample_list = [str(x).strip().lower() for x in self._as_sample_list(sample_names)]
            matched = []
            for dlg in windows:
                try:
                    txt = dlg.window_text().strip().lower()
                    if any(s in txt for s in sample_list):
                        matched.append(dlg)
                except Exception:
                    pass

            if matched:
                if prefer_shortest:
                    matched.sort(key=lambda d: len(d.window_text().strip()))
                    return matched[0]
                return matched[-1]

        # Otherwise use shortest title
        if prefer_shortest:
            windows.sort(key=lambda d: len(d.window_text().strip()))
            return windows[0]

        return windows[-1]
    
    def _get_initial_review_title_info(self, sample_names=None, prefer_shortest=True):
        dlg = self._get_initial_review_dialog(
            sample_names=sample_names,
            prefer_shortest=prefer_shortest,
        )
        title = dlg.window_text().strip()

        matched_sample = None
        if sample_names:
            for s in self._as_sample_list(sample_names):
                if s.strip().lower() in title.lower():
                    matched_sample = s
                    break

        # fallback: use suffix after "InView ReviewData - "
        if matched_sample is None:
            prefix = "InView ReviewData - "
            if title.startswith(prefix):
                matched_sample = title[len(prefix):].strip()
            else:
                matched_sample = title

        return dlg, title, matched_sample


    def get_current_review_title(self, sample_names=None):
        """
        Return the currently visible ReviewData window title.

        If sample_names is provided, prefer a matching one.
        Otherwise return the first visible ReviewData window.
        """
        windows = self.ui.desktop.windows()

        review_titles = []
        for w in windows:
            try:
                txt = w.window_text().strip()
                if txt and "InView ReviewData" in txt:
                    review_titles.append(txt)
            except Exception:
                pass

        if not review_titles:
            raise RuntimeError("No visible ReviewData window found")

        if sample_names:
            sample_names = [str(x).strip().lower() for x in sample_names]
            for title in review_titles:
                tl = title.lower()
                for s in sample_names:
                    if s in tl:
                        return title

        return review_titles[0]  
      
    def wait_for_review_title_update(self, old_title=None, timeout=20, poll=0.5):
        """
        Wait for a ReviewData window to appear.
        If old_title is given, prefer a different title if one appears.
        Otherwise return the currently visible review title.
        """
        import time

        start = time.time()
        last_seen = None

        while time.time() - start < timeout:
            try:
                titles = []
                for w in self.ui.desktop.windows():
                    try:
                        txt = w.window_text().strip()
                        if txt and "InView ReviewData" in txt:
                            titles.append(txt)
                    except Exception:
                        pass

                if titles:
                    if old_title is not None:
                        for t in titles:
                            if t != old_title:
                                return t
                    last_seen = titles[0]
            except Exception:
                pass

            time.sleep(poll)

        if last_seen is not None:
            return last_seen

        raise TimeoutError("No ReviewData window found after waiting")
    

    def _get_review_dialog(self, window_title=None, sample_names=None):
        """
        Return one concrete visible ReviewData dialog wrapper.
        If multiple dialogs share the same title, choose the active one if possible,
        otherwise the last visible match.
        """
        windows = []

        for w in self.ui.desktop.windows():
            try:
                txt = w.window_text().strip()
                if not txt:
                    continue
                if "InView ReviewData" not in txt:
                    continue

                if window_title is not None and txt != window_title:
                    continue

                if sample_names is not None:
                    sample_list = [str(x).strip().lower() for x in self._as_sample_list(sample_names)]
                    if not any(s in txt.lower() for s in sample_list):
                        continue

                wrapper = self.ui.desktop.window(handle=w.handle)
                if wrapper.exists() and wrapper.is_visible():
                    windows.append(wrapper)
            except Exception:
                pass

        if not windows:
            raise RuntimeError("No matching visible ReviewData window found")

        # Prefer focused/active if any
        for dlg in windows:
            try:
                if dlg.has_focus():
                    return dlg
            except Exception:
                pass

        # Otherwise use the last one
        return windows[-1]
    
    def click_review_button(self, button_name, sample_name=None, window_title=None, pause=0.1):
        if window_title is None and sample_name is None:
            raise ValueError("Either sample_name or window_title must be provided")

        dlg = self._get_review_dialog(
            window_title=window_title,
            sample_names=[sample_name] if sample_name is not None else None,
        )

        try:
            dlg.set_focus()
        except Exception:
            pass

        client = dlg.client_rect()
        actual_title = dlg.window_text()

        x_rel, y_rel = self.ui.get_review_button(button_name)
        x = client.left + x_rel
        y = client.top + y_rel

        print(f"[REVIEW CLICK] {button_name} @ ({x}, {y}) in '{actual_title}'")
        self.set_cursor(x, y)
        time.sleep(pause)
        self.left_click()

    
    ###################################################################################
    # Open Helpers
    def open_sample_from_directory(self, directory_path, sample_file_name, dialog_title="Open"):
        controls = self.ui.find_open_dialog_controls()

        address_bar = controls.get("address_bar")
        file_name = controls.get("file_name")
        open_button = controls.get("open_button")

        if address_bar is None:
            raise RuntimeError("Open dialog address bar not found")
        if file_name is None:
            raise RuntimeError("Open dialog file name field not found")
        if open_button is None:
            raise RuntimeError("Open dialog Open button not found")

        # Address bar
        rect = address_bar["rect"]
        self.click_absolute_ui(rect["center_x"], rect["center_y"], window_title=dialog_title, enforcement=0)
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")
        time.sleep(0.2)
        pyautogui.write(str(directory_path), interval=0.03)
        time.sleep(0.2)
        pyautogui.press("enter")
        time.sleep(1.0)

        # File name
        rect = file_name["rect"]
        self.click_absolute_ui(rect["center_x"], rect["center_y"], window_title=dialog_title, enforcement=0)
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")
        time.sleep(0.2)
        pyautogui.write(str(sample_file_name), interval=0.03)
        time.sleep(0.2)

        # Open
        rect = open_button["rect"]
        self.click_absolute_ui(rect["center_x"], rect["center_y"], window_title=dialog_title, enforcement=0)
    
    def save_review_file_as(self, save_dir, save_file_name, dialog_title="Open", wait_after=3):
        controls = self.ui.find_open_dialog_controls()

        address_bar = controls.get("address_bar")
        file_name = controls.get("file_name")
        open_button = controls.get("open_button")

        if address_bar is None or file_name is None or open_button is None:
            raise RuntimeError("Save As dialog controls not found")

        # Address bar
        rect = address_bar["rect"]
        self.click_absolute_ui(rect["center_x"], rect["center_y"], window_title=dialog_title, enforcement=0)
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")
        time.sleep(0.2)
        pyautogui.write(str(save_dir), interval=0.03)
        time.sleep(0.2)
        pyautogui.press("enter")
        time.sleep(1.0)

        # File name
        rect = file_name["rect"]
        self.click_absolute_ui(rect["center_x"], rect["center_y"], window_title=dialog_title, enforcement=0)
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")
        time.sleep(0.2)
        pyautogui.write(str(save_file_name), interval=0.03)
        time.sleep(0.2)

        # Save button is still being detected as open_button by current helper
        rect = open_button["rect"]
        self.click_absolute_ui(rect["center_x"], rect["center_y"], window_title=dialog_title, enforcement=0)
        time.sleep(wait_after)
    ###################################################################################

    # Generic helpers
    import time

    def wait_until(self, predicate, timeout=30, poll=0.3, desc="condition"):
        start = time.time()
        last_err = None

        while time.time() - start < timeout:
            try:
                result = predicate()
                if result:
                    return result
            except Exception as e:
                last_err = e
            time.sleep(poll)

        msg = f"Timed out waiting for {desc} after {timeout}s"
        if last_err is not None:
            msg += f" | last error: {last_err}"
        raise TimeoutError(msg)



    def get_window_text_snapshot(self, window_title):
        dlg = self.ui.desktop.window(title=window_title)
        dlg.wait("exists", timeout=5)
        dlg.wait("visible", timeout=5)

        texts = []

        for c in dlg.descendants():
            try:
                txt = c.window_text().strip()
                if txt:
                    texts.append(txt)
            except Exception:
                pass

        return tuple(texts)
    
    def wait_until_review_changes(self, window_title, before_snapshot, timeout=30, poll=0.5):
        return self.wait_until(
            lambda: self.get_window_text_snapshot(window_title) != before_snapshot,
            timeout=timeout,
            poll=poll,
            desc=f"review window '{window_title}' contents to change"
        )
    

    ###################################################################################



    
    

    

