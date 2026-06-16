"""
Issue #29 splash figures: LinkedIn-optimized hero charts for the big results.
Each figure carries ONE knockout takeaway in its title. V&V palette: slate + amber accent.
Reads data/processed/enriched_systems.csv ; writes outputs/ and assets/.
"""
import csv, random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

INK="#222e38"; SLATE="#3f5d6e"; AMBER="#e0852a"; TEAL="#2b7a8c"; MUTE="#9aa7b0"; LOSS="#c0473b"; GRID="#eef1f3"
plt.rcParams.update({
    "font.family":"sans-serif","font.sans-serif":["Helvetica Neue","Helvetica","Arial","DejaVu Sans"],"figure.facecolor":"white","axes.facecolor":"white",
    "text.color":INK,"axes.labelcolor":INK,"xtick.color":INK,"ytick.color":INK,
    "axes.edgecolor":MUTE,"axes.linewidth":0.8,
})
FOOT=("Vitals & Variables #29   |   Q1-2026 reported operating margins   |   "
      "data: SEC / CMS / AHRQ / Becker's   |   descriptive, n=40, non-random")

rows=list(csv.DictReader(open("data/processed/enriched_systems.csv")))
for r in rows:
    r["m"]=float(r["op_margin_pct"]); r["norm"]=float(r["op_margin_q1_normalized_pct"])
    r["rev"]=float(r["op_revenue_musd"]); r["own"]=r["ownership"]; r["name"]=r["system_name"]
    r["pi"]=float(r["cms_pi_metric"]) if (r.get("cms_pi_metric") or "").strip() else None
byname={r["name"]:r for r in rows}

def finish(fig, path):
    fig.text(0.5,0.015,FOOT,ha="center",va="bottom",fontsize=8.5,color=MUTE)
    for ext in ("outputs","assets"):
        fig.savefig(f"{ext}/{path}",dpi=150,bbox_inches="tight",facecolor="white")
    plt.close(fig)

def despine(ax, keep_left=True):
    for s in ["top","right"]+([] if keep_left else ["left"]):
        ax.spines[s].set_visible(False)

# ---------- FIG 1: ownership ranked bar ----------
rs=sorted(rows,key=lambda r:r["m"])
fig,ax=plt.subplots(figsize=(9.6,12),dpi=150)
ys=list(range(len(rs)))
ax.barh(ys,[r["m"] for r in rs],height=0.74,
        color=[AMBER if r["own"]=="for-profit" else SLATE for r in rs],zorder=3)
for i,r in enumerate(rs):
    ax.text(r["m"]+(0.3 if r["m"]>=0 else -0.3),i,f"{r['m']:+.1f}%",va="center",
            ha="left" if r["m"]>=0 else "right",fontsize=8.6,color=INK,zorder=4)
ax.set_yticks(ys); ax.set_yticklabels([r["name"] for r in rs],fontsize=8.8)
ax.axvline(0,color=MUTE,lw=0.9,zorder=2)
ax.set_xlim(-7.5,27.5); ax.set_xlabel("Q1-2026 operating margin",fontsize=12)
ax.set_xticks(range(-5,30,5)); ax.set_xticklabels([f"{v}%" for v in range(-5,30,5)])
ax.grid(axis="x",color=GRID,lw=1,zorder=0); ax.set_axisbelow(True); despine(ax)
ax.legend(handles=[Patch(color=AMBER,label="For-profit (n=4)"),Patch(color=SLATE,label="Nonprofit (n=36)")],
          loc="lower right",frameon=False,fontsize=11)
fig.suptitle("A 28.6-point margin spread.\nThe top is mostly a tax category.",fontsize=19,fontweight="bold",y=0.985)
ax.set_title("All four for-profits land in the top six. The 36 nonprofits run +10.6% to -4.5%.\n"
             "For-profit average 14.2%      Nonprofit average 2.8%",fontsize=11.5,color=SLATE,pad=10)
fig.tight_layout(rect=[0,0.03,1,0.945])
finish(fig,"splash_1_ownership.png")

# ---------- FIG 2: Tenet one-time gain ----------
fig,ax=plt.subplots(figsize=(9,7.6),dpi=150)
xT,xH=0,1
ax.bar(xT,16.4,width=0.52,color=SLATE,zorder=3,label="Recurring operating margin")
ax.bar(xT,7.7,bottom=16.4,width=0.52,color=AMBER,zorder=3,label="One-time Conifer gain ($413M)")
ax.bar(xH,12.0,width=0.52,color=SLATE,zorder=3)
ax.text(xT,24.1+0.5,"24.1%",ha="center",fontsize=14,fontweight="bold",color=INK)
ax.text(xT,16.4/2,"16.4%",ha="center",va="center",fontsize=12,color="white",fontweight="bold")
ax.text(xT,16.4+7.7/2,"+7.7 pts",ha="center",va="center",fontsize=10.5,color="white",fontweight="bold")
ax.text(xH,12.0+0.5,"12.0%",ha="center",fontsize=13,fontweight="bold",color=INK)
ax.set_xticks([xT,xH]); ax.set_xticklabels(["Tenet (#1)","HCA (#2)"],fontsize=13)
ax.set_ylim(0,27); ax.set_ylabel("Q1-2026 operating margin",fontsize=12)
ax.set_yticks(range(0,30,5)); ax.set_yticklabels([f"{v}%" for v in range(0,30,5)])
ax.grid(axis="y",color=GRID,lw=1,zorder=0); ax.set_axisbelow(True); despine(ax)
# lead annotations
ax.annotate("",xy=(0.62,24.1),xytext=(0.62,12.0),arrowprops=dict(arrowstyle="<->",color=MUTE,lw=1.3))
ax.text(0.66,18.0,"as reported:\n+12.1 pt lead",fontsize=10,color=MUTE,va="center")
ax.annotate("",xy=(1.34,16.4),xytext=(1.34,12.0),arrowprops=dict(arrowstyle="<->",color=AMBER,lw=1.6))
ax.text(1.30,14.2,"normalized:\n+4.4 pt lead",fontsize=10.5,color=AMBER,va="center",ha="right",fontweight="bold")
ax.legend(loc="upper right",frameon=False,fontsize=10.5)
fig.suptitle("Strip one accounting event and the\nrunaway #1 rejoins the pack.",fontsize=19,fontweight="bold",y=0.99)
ax.set_title("Tenet's +24.1% includes a $413M one-time gain from winding down a Conifer contract\n"
             "(its own 8-K). Normalized: 16.4%. Two-thirds of its lead over HCA evaporates.",
             fontsize=11,color=SLATE,pad=10)
fig.tight_layout(rect=[0,0.03,1,0.93])
finish(fig,"splash_2_onetimer.png")

# ---------- FIG 3: digital maturity null ----------
fig,ax=plt.subplots(figsize=(10.4,6.4),dpi=150)
random.seed(29)
trio={"AdventHealth","Bon Secours Mercy Health","Parkview Health"}
others=[r for r in rows if r["name"] not in trio]
ax.scatter([r["m"] for r in others],[random.uniform(-1,1) for _ in others],
           s=46,color=MUTE,alpha=0.55,zorder=2,label="Other 37 systems")
for nm,dy in [("AdventHealth",0.0),("Bon Secours Mercy Health",0.0),("Parkview Health",0.0)]:
    r=byname[nm]; c=LOSS if r["m"]<0 else AMBER
    ax.scatter([r["m"]],[dy],s=320,color=c,edgecolor="white",lw=1.5,zorder=5)
ax.annotate("AdventHealth  +9.3%",(byname["AdventHealth"]["m"],0),xytext=(9.3,0.78),
            fontsize=11,fontweight="bold",color=AMBER,ha="center")
ax.annotate("Bon Secours  +2.6%",(2.6,0),xytext=(2.6,-0.82),fontsize=11,fontweight="bold",color=AMBER,ha="center")
ax.annotate("Parkview  -0.9%",(-0.9,0),xytext=(-0.9,0.78),fontsize=11,fontweight="bold",color=LOSS,ha="center")
ax.axvline(3.91,color=TEAL,lw=1.2,ls="--",zorder=3)
ax.text(3.91,-1.45,"all-40 average +3.9%",color=TEAL,fontsize=9.5,ha="center")
ax.set_xlim(-7,26); ax.set_ylim(-1.7,1.7); ax.set_yticks([])
ax.set_xlabel("Q1-2026 operating margin",fontsize=12)
ax.set_xticks(range(-5,30,5)); ax.set_xticklabels([f"{v}%" for v in range(-5,30,5)])
ax.grid(axis="x",color=GRID,lw=1,zorder=0); ax.set_axisbelow(True); despine(ax,keep_left=False)
ax.legend(loc="upper right",frameon=False,fontsize=10.5)
fig.suptitle("Same top digital tier. Opposite report cards.",fontsize=20,fontweight="bold",y=0.99)
ax.set_title("The three systems at CHIME's 'Level 10' (its top published digital tier, 2025) in amber "
             "span the field,\nfrom -0.9% to +9.3%. Across all 40, margin vs CMS interoperability: r = -0.03 (no relationship).",
             fontsize=11,color=SLATE,pad=10)
fig.tight_layout(rect=[0,0.04,1,0.92])
finish(fig,"splash_3_digital.png")

# ---------- FIG 4: scale doesn't predict margin ----------
fig,ax=plt.subplots(figsize=(9.6,7),dpi=150)
ax.scatter([r["rev"]/1000 for r in rows],[r["m"] for r in rows],
           s=[max(20,(float(r["total_acute_beds"]) if (r.get("total_acute_beds") or "").strip() else 1500)/45) for r in rows],
           color=SLATE,alpha=0.55,edgecolor="white",lw=0.6,zorder=3)
# fit line
xs=np.array([r["rev"]/1000 for r in rows]); yms=np.array([r["m"] for r in rows])
b,a=np.polyfit(xs,yms,1)
xx=np.linspace(0,35,50); ax.plot(xx,a+b*xx,color=MUTE,ls="--",lw=1.4,zorder=2)
for nm,off in [("Kaiser Permanente",(-0.5,2.2)),("HCA Healthcare",(-0.5,2.0)),("Tenet Healthcare",(0.4,1.4))]:
    r=byname[nm]; c=AMBER if r["own"]=="for-profit" else TEAL
    ax.scatter([r["rev"]/1000],[r["m"]],s=180,color=c,edgecolor="white",lw=1.4,zorder=5)
    ax.annotate(f"{nm.split()[0]}\n${r['rev']/1000:.1f}B  ·  {r['m']:+.1f}%",(r["rev"]/1000,r["m"]),
                xytext=(r["rev"]/1000+off[0],r["m"]+off[1]),fontsize=10.5,fontweight="bold",color=c,ha="center")
ax.set_xlim(-1,37); ax.set_xlabel("Q1-2026 operating revenue ($B)",fontsize=12)
ax.set_ylabel("Q1-2026 operating margin",fontsize=12)
ax.set_yticks(range(-5,30,5)); ax.set_yticklabels([f"{v}%" for v in range(-5,30,5)])
ax.axhline(0,color=MUTE,lw=0.8,zorder=1)
ax.grid(color=GRID,lw=1,zorder=0); ax.set_axisbelow(True); despine(ax)
fig.suptitle("The biggest system on the list runs 2.1%.\nOne half its size runs 12%.",fontsize=19,fontweight="bold",y=0.99)
ax.set_title("Operating margin vs revenue, all 40 systems. Scale explains about 1% of the variance (r = 0.11).\n"
             "Bubble size = acute beds.",fontsize=11,color=SLATE,pad=10)
fig.tight_layout(rect=[0,0.03,1,0.93])
finish(fig,"splash_4_scale.png")

print("wrote splash_1_ownership, splash_2_onetimer, splash_3_digital, splash_4_scale to outputs/ and assets/")
