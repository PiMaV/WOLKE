"""
Entry point: python -m wolke (or WOLKE.exe)
Loads config, creates app, starts server, opens browser.
"""
import os
import sys
import webbrowser

from wolke.web.app import create_app


def main() -> None:
    config_path = None
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
        ini = os.path.join(base_dir, "config.ini")
        example = os.path.join(base_dir, "config.ini.example")
        if os.path.isfile(ini):
            config_path = ini
        elif os.path.isfile(example):
            config_path = example
        else:
            print(
                "No config.ini next to the binary. Download config.ini.example "
                "from the GitHub release, copy it here as config.ini, and set db_filename."
            )
            sys.exit(1)
    app, server, socketio, state, config = create_app(config_path)
    port = config.port
    try:
        url = f"http://127.0.0.1:{port}"
        webbrowser.open(url)
        run_kw = {"host": "0.0.0.0", "port": port, "debug": config.debug}
        if getattr(sys, "frozen", False):
            run_kw["allow_unsafe_werkzeug"] = True
        socketio.run(server, **run_kw)
    except OSError as e:
        if getattr(e, "winerror", None) == 10048 or (getattr(e, "errno", None) == 98):
            print(f"Port {port} ist bereits belegt. Anderen Port setzen: set WOLKE_PORT=8051 (Windows) bzw. WOLKE_PORT=8051 uv run python -m wolke")
            sys.exit(1)
        raise


if __name__ == "__main__":
    main()
