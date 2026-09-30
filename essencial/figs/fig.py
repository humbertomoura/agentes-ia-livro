import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
TEAL='#0E7C7B'; ORANGE='#E07A1F'; GRAY='#6B7280'; LTEAL='#E6F2F2'; LOR='#FDF1E6'; LG='#F3F4F6'; DARK='#1F2933'
plt.rcParams['font.family']='DejaVu Sans'

def canvas(w=8,h=4.5):
    fig,ax=plt.subplots(figsize=(w,h),dpi=200); ax.set_xlim(0,w); ax.set_ylim(0,h); ax.axis('off'); return fig,ax
def box(ax,x,y,w,h,text,fc=LTEAL,ec=TEAL,fs=11,bold=False,tc=DARK):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.02,rounding_size=0.12',fc=fc,ec=ec,lw=1.6))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fs,color=tc,weight='bold' if bold else 'normal',wrap=True)
def arrow(ax,x1,y1,x2,y2,c=GRAY,text=None,fs=9,dy=0.12,ls='-'):
    ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='-|>',color=c,lw=1.6,linestyle=ls,shrinkA=2,shrinkB=2))
    if text: ax.text((x1+x2)/2,(y1+y2)/2+dy,text,ha='center',va='bottom',fontsize=fs,color=c)
def save(fig,name):
    fig.savefig(name,bbox_inches='tight',pad_inches=0.08,facecolor='white'); plt.close(fig)
