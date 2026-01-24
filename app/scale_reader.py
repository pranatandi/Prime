"""
Serial port communication module for digital scale indicator.
Supports both real hardware via USB/Serial and mock mode for testing.
"""
import os
import re
import serial
import time
import random
from dotenv import load_dotenv

load_dotenv()


class ScaleReader:
    """Class to handle reading weight from digital scale indicator"""
    
    def __init__(self):
        self.mock_mode = os.getenv('MOCK_SERIAL', 'True').lower() == 'true'
        self.port = os.getenv('SERIAL_PORT', '/dev/ttyUSB0')
        self.baudrate = int(os.getenv('SERIAL_BAUDRATE', '9600'))
        self.bytesize = int(os.getenv('SERIAL_BYTESIZE', '8'))
        self.parity = os.getenv('SERIAL_PARITY', 'N')
        self.stopbits = int(os.getenv('SERIAL_STOPBITS', '1'))
        self.timeout = int(os.getenv('SERIAL_TIMEOUT', '1'))
        self.serial_conn = None
        
    def connect(self):
        """Establish connection to the serial port"""
        if self.mock_mode:
            print("[MOCK MODE] Serial connection simulated")
            return True
        
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.timeout
            )
            print(f"Connected to scale on {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to scale: {e}")
            return False
    
    def disconnect(self):
        """Close the serial connection"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("Disconnected from scale")
    
    def read_weight(self):
        """
        Read weight from the scale indicator.
        Returns weight value as float in kg.
        
        In mock mode, generates random realistic weight values.
        In real mode, reads from serial port and parses the response.
        """
        if self.mock_mode:
            return self._read_mock_weight()
        
        return self._read_real_weight()
    
    def _read_mock_weight(self):
        """Generate mock weight data for testing"""
        # Simulate realistic palm fruit weights (in kg)
        # Gross weight: typically 15,000 - 30,000 kg
        # Tare weight: typically 8,000 - 12,000 kg
        weight = random.uniform(8000, 30000)
        weight = round(weight, 2)
        print(f"[MOCK MODE] Generated weight: {weight} kg")
        return weight
    
    def _read_real_weight(self):
        """
        Read actual weight from serial port.
        
        Common weight indicator formats:
        - "ST,GS,+12345.67kg\r\n"
        - "+12345.67\r\n"
        - "WT:12345.67\r\n"
        
        This implementation handles common formats.
        Adjust parsing logic based on your specific scale model.
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            if not self.connect():
                raise Exception("Cannot connect to scale")
        
        try:
            # Clear any existing data in buffer
            self.serial_conn.reset_input_buffer()
            
            # Some scales need a command to send weight
            # Uncomment if your scale requires it:
            # self.serial_conn.write(b'W\r\n')
            
            # Read response
            response = self.serial_conn.readline()
            
            if not response:
                raise Exception("No response from scale")
            
            # Decode and clean the response
            response_str = response.decode('ascii', errors='ignore').strip()
            print(f"Scale response: {response_str}")
            
            # Parse weight from response
            weight = self._parse_weight_from_response(response_str)
            
            return weight
            
        except Exception as e:
            print(f"Error reading weight: {e}")
            raise
    
    def _parse_weight_from_response(self, response):
        """
        Parse weight value from scale response string.
        Handles various common formats.
        """
        # Remove common prefixes and suffixes
        response = response.replace('ST,GS,', '')
        response = response.replace('WT:', '')
        response = response.replace('kg', '')
        response = response.replace('KG', '')
        
        # Extract numeric value (including decimal and sign)
        match = re.search(r'[+-]?\d+\.?\d*', response)
        
        if match:
            weight_str = match.group()
            weight = float(weight_str)
            return abs(weight)  # Return absolute value
        else:
            raise ValueError(f"Cannot parse weight from response: {response}")
    
    def test_connection(self):
        """Test the serial connection and read a sample weight"""
        try:
            if self.connect():
                weight = self.read_weight()
                print(f"Test successful. Weight reading: {weight} kg")
                self.disconnect()
                return True, weight
            else:
                return False, None
        except Exception as e:
            print(f"Test failed: {e}")
            return False, None


# Utility functions for easy import
def get_scale_reader():
    """Get a ScaleReader instance"""
    return ScaleReader()


def read_scale_weight():
    """Quick function to read weight from scale"""
    reader = ScaleReader()
    try:
        reader.connect()
        weight = reader.read_weight()
        return weight
    finally:
        reader.disconnect()


if __name__ == '__main__':
    # Test the scale reader
    print("Testing Scale Reader...")
    reader = ScaleReader()
    success, weight = reader.test_connection()
    
    if success:
        print(f"✓ Scale reader working correctly. Sample weight: {weight} kg")
    else:
        print("✗ Scale reader test failed")
