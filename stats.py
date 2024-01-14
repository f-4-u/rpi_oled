import sys
import socket
import RPi.GPIO as GPIO
import time
import psutil
from datetime import timedelta
from PIL import ImageFont
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

# Set the GPIO mode to BCM (Broadcom SOC channel numbering)
GPIO.setmode(GPIO.BCM)

# Set the pin number connected to the touch sensor
TOUCH_PIN = 12

# Set the GPIO pin as an input
GPIO.setup(TOUCH_PIN, GPIO.IN)

# Variable to track the touch sensor state
prev_touch_state = GPIO.LOW  # Assuming the sensor is not touched initially

# Variable to store the last time the button was pressed
last_button_press_time = time.time()

# Minimum time interval between button presses to prevent bouncing
MIN_BUTTON_PRESS_INTERVAL = 0.5  # Adjust this value as needed

# OLED display configuration
serial = i2c(port=1, address=0x3C)  # Update the I2C address if needed
device = ssd1306(serial, rotate=0)

font = ImageFont.truetype('/opt/display/dogicapixel.ttf', 8)


host_booted = psutil.boot_time()

# Your existing rendering functions
def render_device_info(draw):
    h_name = socket.gethostname()
    ip_address = socket.gethostbyname(h_name)
    uptime = timedelta(seconds=int(time.time() - host_booted))

    draw.text((0, 0),       f'Host: {h_name}', font=font, fill="white")
    draw.text((0, 12),    f'Ip: {ip_address}', font=font, fill="white")
    draw.text((0, 24),     f'Uptime: {uptime}', font=font, fill="white")  
      
def render_overview(draw):
    ram = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    CPU = psutil.cpu_percent(interval=1)
    RAM = f"Free: {format_size(ram.available)} Used: {format_size(ram.used)}"
    SWAP = f"Free: {format_size(swap.free)} Used: {format_size(swap.used)}"
        
    draw.text((0, 0),    f'CPU Ussage: {CPU}', font=font, fill="white")
    draw.text((0, 12),    f'RAM: {RAM}',  font=font, fill="white")
    draw.text((0, 24),    f'Swap: {SWAP}',  font=font, fill="white")

def render_cpu(draw):
   # CPU usage percentage for each core
    cpu_percent_per_core = psutil.cpu_percent(percpu=True)

    # Total CPU usage
    total_cpu_percent = psutil.cpu_percent()

    # CPU frequency
    cpu_frequency = psutil.cpu_freq()

    # Number of CPU cores
    num_cores = psutil.cpu_count(logical=False)
    num_logical_cores = psutil.cpu_count(logical=True)

    # Render CPU stats on the display
    for core, percent in enumerate(cpu_percent_per_core):
        draw.text((0, 0 + core * 8), f"Core {core + 1}: {percent}%", font=font, fill="white")

    draw.text((0, 35 + num_cores * 0), f"Total: {total_cpu_percent}%", font=font, fill="white")
    draw.text((0, 45 + num_cores * 0), f"Frequency: {cpu_frequency.current} MHz", font=font, fill="white")

# Function to render RAM and Swap usage stats as a diagram on the display
def render_memory(draw):
    # Get RAM usage
    ram = psutil.virtual_memory()

    # Get Swap usage
    swap = psutil.swap_memory()

    # Render RAM and Swap stats as a diagram on the display with the smaller font

    # Render RAM usage bar
    ram_bar_length = int((ram.percent / 100) * 128)  # Scale to the display width
    draw.rectangle((0, 0, ram_bar_length, 10), outline="white", fill="white")
    draw.text((2, 12), f"RAM: {ram.percent}% \n({format_size(ram.used)}/{format_size(ram.total)})", font=font, fill="white")

    # Render Swap usage bar
    swap_bar_length = int((swap.percent / 100) * 128)  # Scale to the display width
    draw.rectangle((0, 30, swap_bar_length, 40), outline="white", fill="white")
    draw.text((2, 42), f"Swap: {swap.percent}% \n({format_size(swap.used)}/{format_size(swap.total)})", font=font, fill="white")

def render_fs(draw):
    # Get information about all partitions
    partitions = psutil.disk_partitions()

    # Render filesystem stats for each partition on the display
    y_position = 0
    for partition in partitions:
        partition_usage = psutil.disk_usage(partition.mountpoint)

        draw.text((0, y_position), f"{partition.device}", font=font, fill="white")
        draw.text((0, y_position + 10), f"Total: {format_size(partition_usage.total)}", font=font, fill="white")
        draw.text((0, y_position + 20), f"Used: {format_size(partition_usage.used)}", font=font, fill="white")
        draw.text((0, y_position + 30), f"Free: {format_size(partition_usage.free)}", font=font, fill="white")
        draw.text((0, y_position + 40), f"Usage: {partition_usage.percent}%", font=font, fill="white")

        y_position += 60  # Adjust the vertical spacing as needed

# Function to format bytes into human-readable format
def format_size(size):
    power = 2**10
    n = 0
    size_format = "Bytes"

    while size > power:
        size /= power
        n += 1

    size_format = f"{size:.2f} {['Bytes', 'KB', 'MB', 'GB', 'TB'][n]}"

    return size_format

# Global variable to prevent multiple presses during button hold
button_pressed = False

# Debounce time in seconds
DEBOUNCE_TIME = 0.3

# Time interval for page cycling in seconds
PAGE_CYCLE_INTERVAL = 5

# Function to check touch sensor state
def check_touch_state():
    return GPIO.input(TOUCH_PIN)

# Callback function for touch sensor
def touch_callback():
    global button_pressed, last_button_press_time, last_page_change_time
    current_time = time.time()
    
    # Check if the minimum interval between button presses has passed
    if current_time - last_button_press_time >= MIN_BUTTON_PRESS_INTERVAL:
        button_pressed = True
        last_button_press_time = current_time
        last_page_change_time = current_time  # Reset the page timer
        render_next_page()

# Function to render the current page
def render_page(page, render_functions):
    render_function = render_functions.get(page, None)
    if render_function:
        with canvas(device) as draw:
            render_function(draw)
    else:
        print(f"No rendering function found for page {page}")

# Function to render the next page
def render_next_page():
    global current_page
    current_page = (current_page + 1) % len(page_render_functions)

# Main loop
current_page = 0
last_page_change_time = time.time()

# Define rendering functions for each page
page_render_functions = {
    0: render_device_info,
    1: render_overview,
    2: render_cpu,
    3: render_memory,
    4: render_fs,
    # Add more pages as needed
}

try:
    while True:       
        # Check touch sensor state
        current_touch_state = check_touch_state()

        # Detect falling edge (change from HIGH to LOW)
        if prev_touch_state == GPIO.HIGH and current_touch_state == GPIO.LOW:
            touch_callback()

        prev_touch_state = current_touch_state

        # Check if it's time to cycle pages
        current_time = time.time()
        if current_time - last_page_change_time >= PAGE_CYCLE_INTERVAL:
            last_page_change_time = current_time
            render_next_page()

        # Render the current page
        render_page(current_page, page_render_functions)
        time.sleep(0.1)  # Adjust the sleep duration as needed

except KeyboardInterrupt:
    pass  # Handle Ctrl+C gracefully

except Exception as e:
    print(f"Error in main loop: {e}")

finally:
    GPIO.cleanup()  # Ensure GPIO cleanup is executed whether an exception occurs or not
    sys.exit(1)  # Exit the program
