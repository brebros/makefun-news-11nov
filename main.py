import os

src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "summary.txt")
out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(out_dir, exist_ok=True)
with open(src, "rb") as f:
    data = f.read()
with open(os.path.join(out_dir, "entry.txt"), "wb") as f:
    f.write(data)
print("wrote", os.path.join(out_dir, "entry.txt"), len(data), "chars")
