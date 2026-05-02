"""
Test Raspberry Pi Server - Mock Flask server for development/testing

This simulates a Raspberry Pi Flask server running at a traffic junction.
Use this for testing the command execution system without real hardware.

Run: python test_rpi_server.py
"""
from flask import Flask, request, jsonify
from datetime import datetime
import time

app = Flask(__name__)

# Configuration
API_KEY = "dev-api-key"
PORT = 5000

# Simulated state
state = {
    "mode": "manual",
    "lane_states": {
        "lane1": "red",
        "lane2": "red",
        "lane3": "red",
        "lane4": "red"
    },
    "timings": {
        "lane1": 30,
        "lane2": 30,
        "lane3": 30,
        "lane4": 30
    },
    "vip_active": False,
    "lanes_to_green": [],
    "emergency_stop": False
}


def check_api_key():
    """Validate API key from request headers"""
    api_key = request.headers.get('X-API-KEY')
    if api_key != API_KEY:
        return jsonify({
            "success": False,
            "error": "Unauthorized - Invalid API key"
        }), 401
    return None


def get_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat() + "Z"


@app.route('/mode/<mode_name>', methods=['POST'])
def set_mode(mode_name):
    """
    Set traffic mode
    
    POST /mode/{mode_name}
    
    Modes: auto, manual, blinker, emergency
    """
    # Check API key
    error = check_api_key()
    if error:
        return error
    
    # Validate mode
    valid_modes = ['auto', 'manual', 'blinker', 'emergency']
    if mode_name not in valid_modes:
        return jsonify({
            "success": False,
            "error": f"Invalid mode. Must be one of: {', '.join(valid_modes)}"
        }), 400
    
    # Update state
    state["mode"] = mode_name
    
    # Handle emergency mode
    if mode_name == "emergency":
        state["emergency_stop"] = True
        state["lane_states"] = {
            "lane1": "red",
            "lane2": "red",
            "lane3": "red",
            "lane4": "red"
        }
    else:
        state["emergency_stop"] = False
    
    print(f"[{get_timestamp()}] Mode changed to: {mode_name}")
    
    return jsonify({
        "success": True,
        "mode": mode_name,
        "timestamp": get_timestamp()
    })


@app.route('/api/set_manual_times', methods=['POST'])
def set_manual_times():
    """
    Set manual lane timings
    
    POST /api/set_manual_times
    Body: {
        "lane1_time": 30,
        "lane2_time": 45,
        "lane3_time": 30,
        "lane4_time": 45
    }
    """
    # Check API key
    error = check_api_key()
    if error:
        return error
    
    # Get request data
    data = request.json
    if not data:
        return jsonify({
            "success": False,
            "error": "Request body is required"
        }), 400
    
    # Validate required fields
    required_fields = ['lane1_time', 'lane2_time', 'lane3_time', 'lane4_time']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing required field: {field}"
            }), 400
    
    # Validate timing values (5-120 seconds)
    for field in required_fields:
        value = data[field]
        if not isinstance(value, (int, float)) or value < 5 or value > 120:
            return jsonify({
                "success": False,
                "error": f"Invalid timing for {field}. Must be between 5 and 120 seconds"
            }), 400
    
    # Update state
    state["timings"] = {
        "lane1": data['lane1_time'],
        "lane2": data['lane2_time'],
        "lane3": data['lane3_time'],
        "lane4": data['lane4_time']
    }
    
    print(f"[{get_timestamp()}] Manual times updated: {state['timings']}")
    
    return jsonify({
        "success": True,
        "timings": state["timings"],
        "timestamp": get_timestamp()
    })


@app.route('/api/vip_override', methods=['POST'])
def vip_override():
    """
    VIP mode override
    
    POST /api/vip_override
    Body: {
        "active": true,
        "lanes_to_green": ["81", "82"]
    }
    """
    # Check API key
    error = check_api_key()
    if error:
        return error
    
    # Get request data
    data = request.json
    if not data:
        return jsonify({
            "success": False,
            "error": "Request body is required"
        }), 400
    
    # Validate required fields
    if 'active' not in data:
        return jsonify({
            "success": False,
            "error": "Missing required field: active"
        }), 400
    
    active = data['active']
    lanes_to_green = data.get('lanes_to_green', [])
    
    # Update state
    state["vip_active"] = active
    state["lanes_to_green"] = lanes_to_green
    
    # Update lane states if VIP is active
    if active:
        # Set all lanes to red first
        state["lane_states"] = {
            "lane1": "red",
            "lane2": "red",
            "lane3": "red",
            "lane4": "red"
        }
        
        # Set specified lanes to green
        for lane in lanes_to_green:
            # Convert "81" -> "lane1", "82" -> "lane2", etc.
            if lane in ["81", "1"]:
                state["lane_states"]["lane1"] = "green"
            elif lane in ["82", "2"]:
                state["lane_states"]["lane2"] = "green"
            elif lane in ["83", "3"]:
                state["lane_states"]["lane3"] = "green"
            elif lane in ["84", "4"]:
                state["lane_states"]["lane4"] = "green"
    
    print(f"[{get_timestamp()}] VIP mode: {active}, Lanes: {lanes_to_green}")
    
    return jsonify({
        "success": True,
        "vip_active": active,
        "lanes_to_green": lanes_to_green,
        "timestamp": get_timestamp()
    })


@app.route('/status', methods=['GET'])
def get_status():
    """
    Get current junction status
    
    GET /status
    """
    # Check API key
    error = check_api_key()
    if error:
        return error
    
    print(f"[{get_timestamp()}] Status requested")
    
    return jsonify({
        "success": True,
        "mode": state["mode"],
        "lane_states": state["lane_states"],
        "timings": state["timings"],
        "vip_active": state["vip_active"],
        "lanes_to_green": state["lanes_to_green"],
        "emergency_stop": state["emergency_stop"],
        "timestamp": get_timestamp()
    })


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    GET /health
    """
    return jsonify({
        "success": True,
        "status": "healthy",
        "timestamp": get_timestamp()
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Test Raspberry Pi Server")
    print("=" * 60)
    print(f"API Key: {API_KEY}")
    print(f"Port: {PORT}")
    print("\nAvailable Endpoints:")
    print("  POST /mode/<mode_name>")
    print("  POST /api/set_manual_times")
    print("  POST /api/vip_override")
    print("  GET  /status")
    print("  GET  /health")
    print("\nStarting server...")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=True
    )
