"""
Mock Control System for Testing
Simple Flask server that simulates the external control system
"""
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# State
current_state = {
    "mode": "manual",
    "lane1": 30,
    "lane2": 45,
    "lane3": 30,
    "lane4": 45,
    "vip_active": False,
    "vip_lanes": [],
    "last_updated": datetime.utcnow().isoformat()
}

# API Key validation
VALID_API_KEY = "dev-api-key"


def check_api_key():
    """Check if API key is valid"""
    api_key = request.headers.get('X-API-KEY')
    if api_key != VALID_API_KEY:
        return jsonify({"error": "Invalid API key"}), 401
    return None


@app.route('/switch_mode', methods=['POST'])
def switch_mode():
    """Switch traffic control mode"""
    auth_error = check_api_key()
    if auth_error:
        return auth_error
    
    data = request.json
    mode = data.get('mode')
    
    if not mode:
        return jsonify({"error": "Mode is required"}), 400
    
    valid_modes = ['manual', 'auto_circle', 'auto_jump', 'blinker', 'vip']
    if mode not in valid_modes:
        return jsonify({"error": f"Invalid mode. Must be one of: {', '.join(valid_modes)}"}), 400
    
    current_state['mode'] = mode
    current_state['last_updated'] = datetime.utcnow().isoformat()
    
    print(f"[CONTROL] Mode switched to: {mode}")
    
    return jsonify({
        "status": "ok",
        "mode": mode,
        "message": f"Mode switched to {mode}"
    })


@app.route('/set_manual_times', methods=['POST'])
def set_manual_times():
    """Set manual timing for all lanes"""
    auth_error = check_api_key()
    if auth_error:
        return auth_error
    
    data = request.json
    
    # Validate lanes
    for lane in ['lane1', 'lane2', 'lane3', 'lane4']:
        if lane not in data:
            return jsonify({"error": f"{lane} is required"}), 400
        
        time_value = data[lane]
        if not isinstance(time_value, int) or time_value < 5 or time_value > 300:
            return jsonify({"error": f"{lane} must be between 5 and 300 seconds"}), 400
    
    # Update state
    current_state['lane1'] = data['lane1']
    current_state['lane2'] = data['lane2']
    current_state['lane3'] = data['lane3']
    current_state['lane4'] = data['lane4']
    current_state['mode'] = 'manual'
    current_state['last_updated'] = datetime.utcnow().isoformat()
    
    print(f"[CONTROL] Manual times set: L1={data['lane1']}s, L2={data['lane2']}s, L3={data['lane3']}s, L4={data['lane4']}s")
    
    return jsonify({
        "status": "ok",
        "timings": {
            "lane1": data['lane1'],
            "lane2": data['lane2'],
            "lane3": data['lane3'],
            "lane4": data['lane4']
        },
        "message": "Manual times set successfully"
    })


@app.route('/vip_override', methods=['POST'])
def vip_override():
    """Activate or deactivate VIP override mode"""
    auth_error = check_api_key()
    if auth_error:
        return auth_error
    
    data = request.json
    
    if 'active' not in data:
        return jsonify({"error": "active field is required"}), 400
    
    active = data['active']
    lanes_to_green = data.get('lanes_to_green', [])
    
    # Validate lanes
    if active and lanes_to_green:
        for lane in lanes_to_green:
            if not isinstance(lane, int) or lane < 1 or lane > 4:
                return jsonify({"error": "Lane numbers must be between 1 and 4"}), 400
    
    # Update state
    current_state['vip_active'] = active
    current_state['vip_lanes'] = lanes_to_green if active else []
    current_state['mode'] = 'vip' if active else 'manual'
    current_state['last_updated'] = datetime.utcnow().isoformat()
    
    if active:
        print(f"[CONTROL] VIP mode activated: lanes={lanes_to_green}")
    else:
        print(f"[CONTROL] VIP mode deactivated")
    
    return jsonify({
        "status": "ok",
        "vip_active": active,
        "lanes": lanes_to_green,
        "message": f"VIP mode {'activated' if active else 'deactivated'}"
    })


@app.route('/status', methods=['GET'])
def get_status():
    """Get current status"""
    auth_error = check_api_key()
    if auth_error:
        return auth_error
    
    return jsonify({
        "status": "ok",
        "mode": current_state['mode'],
        "lane1": current_state['lane1'],
        "lane2": current_state['lane2'],
        "lane3": current_state['lane3'],
        "lane4": current_state['lane4'],
        "vip_active": current_state['vip_active'],
        "vip_lanes": current_state['vip_lanes'],
        "last_updated": current_state['last_updated'],
        "health": "ok"
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Control system is healthy",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/emergency_stop', methods=['POST'])
def emergency_stop():
    """Emergency stop - set all signals to blinker"""
    auth_error = check_api_key()
    if auth_error:
        return auth_error
    
    current_state['mode'] = 'blinker'
    current_state['vip_active'] = False
    current_state['vip_lanes'] = []
    current_state['last_updated'] = datetime.utcnow().isoformat()
    
    print(f"[CONTROL] EMERGENCY STOP - All signals set to blinker")
    
    return jsonify({
        "status": "ok",
        "mode": "blinker",
        "message": "Emergency stop activated"
    })


@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        "name": "ITMS Mock Control System",
        "version": "1.0.0",
        "endpoints": [
            "POST /switch_mode",
            "POST /set_manual_times",
            "POST /vip_override",
            "GET /status",
            "GET /health",
            "POST /emergency_stop"
        ],
        "authentication": "X-API-KEY header required"
    })


if __name__ == '__main__':
    print("=" * 60)
    print("ITMS Mock Control System")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("API Key: dev-api-key")
    print("=" * 60)
    print("\nAvailable endpoints:")
    print("  POST /switch_mode")
    print("  POST /set_manual_times")
    print("  POST /vip_override")
    print("  GET  /status")
    print("  GET  /health")
    print("  POST /emergency_stop")
    print("=" * 60)
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
