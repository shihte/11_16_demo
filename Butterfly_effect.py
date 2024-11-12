import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from scipy.integrate import odeint

# Lorenz方程
def lorenz(w, t, p, r, b): 
    x, y, z = w
    return np.array([p*(y-x), x*(r-z)-y, x*y-b*z]) 

# 設置參數
p, r, b = 10.0, 28.0, 3.0
t = np.arange(0, 20.0, 0.01)  # 延長時間以更好地觀察效應

# 創建多個初始條件略微不同的軌跡
num_trajectories = 5
initial_z_values = np.linspace(10.0, 10.2, num_trajectories)
tracks = []

for z0 in initial_z_values:
    track = odeint(lorenz, (1.0, 1.0, z0), t, args=(p, r, b))
    tracks.append(track)  # 不進行轉置

# 創建圖形
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# 設置坐標軸
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_xlim3d([-20.0, 20.0])
ax.set_ylim3d([-25.0, 25.0])
ax.set_zlim3d([0.0, 50.0])
ax.set_title('Butterfly Effect in Lorenz System\nInitial conditions differ by 0.05 in z')

# 創建每個軌跡的小球和線
colors = plt.cm.rainbow(np.linspace(0, 1, num_trajectories))
balls = []
lines = []

for color in colors:
    ball, = ax.plot([], [], [], linestyle='None', marker='o',
                   markersize=8, markeredgecolor=color,
                   color='white', markeredgewidth=2)
    line, = ax.plot([], [], [], color=color, alpha=0.8, linewidth=1)
    balls.append(ball)
    lines.append(line)

# 添加文字說明
time_text = ax.text2D(0.02, 0.95, '', transform=ax.transAxes)

def init():
    for ball, line in zip(balls, lines):
        ball.set_data([], [])
        ball.set_3d_properties([])
        line.set_data([], [])
        line.set_3d_properties([])
    time_text.set_text('')
    return balls + lines + [time_text]

def animate(frame):
    # 更新每個軌跡
    for j, (ball, line, track) in enumerate(zip(balls, lines, tracks)):
        # 更新球的位置
        x, y, z = track[frame, 0], track[frame, 1], track[frame, 2]
        ball.set_data([x], [y])
        ball.set_3d_properties([z])
        
        # 更新軌跡線
        line.set_data(track[:frame+1, 0], track[:frame+1, 1])
        line.set_3d_properties(track[:frame+1, 2])
    
    # 更新時間文字
    time_text.set_text(f'Time: {t[frame]:.2f}')
    
    # 動態調整視角
    ax.view_init(30, 0.3 * frame)
    
    return balls + lines + [time_text]

# 創建動畫
anim = animation.FuncAnimation(fig, animate,
                             init_func=init,
                             frames=len(t),
                             interval=20,
                             blit=True)

# 添加說明文字
plt.figtext(0.02, 0.02, 'Each trajectory starts with slightly different initial conditions\n'
            'demonstrating how small differences grow over time', 
            fontsize=8, color='gray')

# 顯示動畫
plt.show()