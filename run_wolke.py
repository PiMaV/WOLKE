"""
Launcher for PyInstaller-built EXE. Do not use when running as python -m wolke.
"""
if __name__ == "__main__":
    from wolke.__main__ import main
    main()
