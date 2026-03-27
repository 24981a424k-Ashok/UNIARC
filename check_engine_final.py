from src.database.models import engine
import os

out = "engine_check.txt"
with open(out, 'w') as f:
    f.write(f"Engine URL: {engine.url}\n")
    f.write(f"Absolute Path of Engine URL: {os.path.abspath(str(engine.url).replace('sqlite:///', ''))}\n")
    f.write(f"CWD: {os.getcwd()}\n")

print(f"Results in {out}")
