import PyInstaller.__main__ as pi_main
import os

if __name__ == "__main__":
	pi_main.run([
		"--name=osr情報変更プログラム",
		"--onefile",
		"--console",
		"index.py",
	])
