import pandas as pd
import matplotlib.pyplot as plt
import os


dt = "2025_01_29__01_06_02"

src_dir = f"results/{dt}"


df1 = pd.read_csv(f"{src_dir}/lap_2.csv")
df2 = pd.read_csv(f"{src_dir}/lap_3.csv")
# df3 = pd.read_csv(f"{src_dir}/lap_4.csv")

imgs_dir = f"images/{dt}"
os.makedirs(imgs_dir)


for param in ["speed", "gear", "rpm", "throttle", "brake"]:
    plt.plot(df1[param], label="lap 1")
    plt.plot(df2[param], label="lap 2")
    # plt.plot(df3[param], label="lap 3")
    plt.title(param.capitalize())
    plt.legend(loc="lower right")
    plt.savefig(f"{imgs_dir}/{param}.png")
    plt.clf()

plt.plot(df1["x"], -df1["y"], label="lap 1")
plt.plot(df2["x"], -df2["y"], label="lap 2")
plt.title("Траектория")
plt.legend(loc="lower right")
plt.savefig(f"{imgs_dir}/traj.png")
plt.clf()