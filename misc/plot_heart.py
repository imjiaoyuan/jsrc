import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def LoveFunc():
    font_path = '/usr/share/fonts/windows-fonts/times.ttf'
    fm.fontManager.addfont(font_path)
    
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['mathtext.fontset'] = 'stix'
    
    x = np.arange(-1.8, 1.8, 0.005)
    
    plt.figure(figsize=(12, 10))
    plt.grid(True)
    plt.axis([-3, 3, -2, 4])
    
    plt.text(0, 3.3, r'$f(x)=x^{\frac{2}{3}}+0.9(3.3-x^2)^{\frac{1}{2}}\sin(\alpha\pi x)$',
             fontsize=52, ha='center')
    
    txt2 = plt.text(-0.35, 2.9, '', fontsize=52, ha='left')
    
    line, = plt.plot([], [], linewidth=3.5, color='#CD5555')
    
    for a in np.arange(1, 20.01, 0.01):
        y = (x**2)**(1/3) + 0.9 * np.sqrt(3.3 - x**2) * np.sin(a * np.pi * x)
        
        line.set_data(x, y)
        txt2.set_text(r'$\alpha=' + "{:.2f}".format(a) + r'$')
        
        plt.pause(0.003)
    
    plt.show()

if __name__ == "__main__":
    LoveFunc()