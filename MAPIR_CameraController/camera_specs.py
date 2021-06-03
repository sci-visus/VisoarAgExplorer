class CameraSpecs(object):

    specs = {
        "Kernel 1.2": {
            "calibration": {
                "filters": [
                    "405", "450", "490", "518", "550", "590", "615", "632",
                    "650", "685", "725", "780", "808", "850", "880", "940", "945"
                ],
                "lenses": []
            }
        }, #Remove
        "Kernel 3.2": {
            "calibration": {
                "filters": [
                    "405", "450", "490", "518", "550", "590", "615", "632",
                    "650", "685", "725", "780", "808", "850", "880", "940", "945"
                ],
                # "filters": [
                #     "250", "350", "390", "405", "450", "490", "510", "518", "550", "590", "615", "632", "650",
                #     "685", "709", "725", "750", "780", "808", "830", "850", "880", "940", "945", "1000"
                # ],
                "lenses": []
            },
            "pre_process": {
                "filters": [
                    "250", "350", "390", "405", "450", "490", "510", "518", "550", "590", "615", "632", "650",
                    "685", "709", "725", "750", "780", "808", "830", "850", "880", "940", "945", "1000", "NO FILTER"
                ],
                "lenses": ["3.5mm", "5.5mm", "9.6mm", "12.0mm", "16.0mm", "35.0mm"],
                "enable_filter_select": True,
                "enable_lens_select": True,
                "enable_dark_box": True
            }
        },
        "Kernel 14.4": {
            "calibration": {
                "filters": ["550/660/850", "475/550/850", "644 (RGB)", "850", "OCN"],
                # "filters": ["RGB", "OCN", "RGN", "NGB"],
                "lenses": []
            },
            "pre_process": {
                # "filters": ["550/660/850", "475/550/850", "644 (RGB)", "850", "OCN", "NO FILTER"],
                "filters": ["RGB", "OCN", "RGN", "NGB", "NO FILTER"],
                "lenses": ["3.37mm", "8.25mm"],
                "enable_filter_select": True,
                "enable_lens_select": True,
                "enable_dark_box": True
            }
        },
        "Survey3": {
            "calibration": {
                "filters": ["OCN", "RGN", "NGB", "RE", "NIR"],
                "lenses": [" 3.37mm (Survey3W)", "8.25mm (Survey3N)"]
            },
            "pre_process": {
                "filters": ["RGB", "OCN", "RGN", "NGB", "RE", "NIR"],
                "lenses": ["3.37mm (Survey3W)", "8.25mm (Survey3N)"],
                "enable_filter_select": True,
                "enable_lens_select": True,
                "enable_dark_box": True
            }
        },
        "Survey2": {
            "calibration": {
                "filters": ["Red + NIR (NDVI)", "NIR", "Red", "Green", "Blue", "RGB"],
                "lenses": ["3.97mm"]
            },
            "pre_process": {
                "filters": ["Red + NIR (NDVI)", "NIR", "Red", "Green", "Blue", "RGB"],
                "lenses": ["3.97mm"],
                "enable_filter_select": True,
                "enable_lens_select": False,
                "enable_dark_box": True
            }
        },
        "Survey1": {
            "calibration": {
                "filters": ["Blue + NIR (NDVI)"],
                "lenses": ["3.97mm"]
            },
            "pre_process": {
                "filters": ["Blue + NIR (NDVI)"],
                "lenses": ["3.97mm"],
                "enable_filter_select": False,
                "enable_lens_select": False,
                "enable_dark_box": False
            }
        },
        "DJI Phantom 4": {
            "calibration": {
                "filters": ["Red + NIR (NDVI)", "RGN"],
                "lenses": ["3.97mm"]
            },
            "pre_process": {
                "filters": ["Red + NIR (NDVI)"],
                "lenses": ["3.97mm"],
                "enable_filter_select": False,
                "enable_lens_select": False,
                "enable_dark_box": False
            }
        },
        "DJI Phantom 4 Pro": {
            "calibration": {
                "filters": ["Red + NIR (NDVI)", "RGN"],
                "lenses": ["3.97mm"]
            },
            "pre_process": {
                "filters": ["RGN"],
                "lenses": ["3.97mm"],
                "enable_filter_select": False,
                "enable_lens_select": False,
                "enable_dark_box": False
            }
        },
        "DJI Phantom 3a": {
            "calibration": {
                "filters": ["RGN"],
                "lenses": ["3.97mm"]
            },
            "pre_process": {
                "filters": ["Red + NIR (NDVI)"],
                "lenses": ["3.97mm"],
                "enable_filter_select": False,
                "enable_lens_select": False,
                "enable_dark_box": False
            }
        },
        "DJI Phantom 3p": {
            "calibration": {
                "filters": ["Red + NIR (NDVI)"],
                "lenses": ["3.97mm"]
            },
            "pre_process": {
                "filters": ["Red + NIR (NDVI)"],
                "lenses": ["3.97mm"],
                "enable_filter_select": False,
                "enable_lens_select": False,
                "enable_dark_box": False
            }
        },
        "DJI X3": {
            "calibration": {
                "filters": ["Red + NIR (NDVI)"],
                "lenses": ["3.97mm"]
            },
            "pre_process": {
                "filters": ["Red + NIR (NDVI)"],
                "lenses": ["3.97mm"],
                "enable_filter_select": False,
                "enable_lens_select": False,
                "enable_dark_box": False
            }
        },
    }
