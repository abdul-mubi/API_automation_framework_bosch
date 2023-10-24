taskkill /im python.exe
timeout 2
start python start_data_generator.py --device DEMO_DEVICE_001 --route Route3 --speed 60 --variance 10
timeout 2
start python start_data_generator.py --device DEMO_DEVICE_002 --route Route3 --speed 80 --variance 10
timeout 2
start python start_data_generator.py --device DEMO_DEVICE_003 --route Route3 --speed 60 --variance 10
timeout 2
start python start_data_generator.py --device DEMO_DEVICE_004 --route Route2 --speed 90 --variance 10
timeout 2
start python start_data_generator.py --device DEMO_DEVICE_005 --route Route2 --speed 120 --variance 10