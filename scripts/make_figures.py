from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
R=json.loads((ROOT/'results/summary_v1.json').read_text(encoding='utf-8'))
F=ROOT/'figures';F.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.7,'xtick.major.width':.6,'ytick.major.width':.6,'svg.fonttype':'none','pdf.fonttype':42})
blue='#3E5568'; green='#597E76';rust='#A36657';gray='#D6DEE1';ink='#25343E'
def finish(fig,stem):
 fig.savefig(F/(stem+'.svg'))
 fig.savefig(F/(stem+'.pdf'))
 fig.savefig(F/(stem+'.png'),dpi=300)
 fig.savefig(F/(stem+'.tif'),dpi=1200 if stem=='Figure_1' else 600,pil_kwargs={'compression':'tiff_lzw'})
 im=Image.open(F/(stem+'.png')).convert('RGB'); im.save(F/(stem+'.jpg'),quality=96,dpi=(300,300))
 plt.close(fig)

fig=plt.figure(figsize=(7.35,3.9));gs=fig.add_gridspec(1,2,width_ratios=[1,1.02],left=.18,right=.985,bottom=.22,top=.87,wspace=.50)
ax=fig.add_subplot(gs[0,0]); rows=[]
for rule,cl,yy in [('empirical90',1,3.7),('assured90',1,2.8),('empirical90',0,1.2),('assured90',0,.3)]:
 m=R['full_sample'][rule];vals=[m['tp'] if cl else m['tn'],m['gray_csf_positive'] if cl else m['gray_csf_negative'],m['fn'] if cl else m['fp']];den=99 if cl else 77
 left=0
 for val,col in zip(vals,[blue,gray,rust]):
  ax.barh(yy,100*val/den,left=left,height=.55,color=col,edgecolor='white',linewidth=.5)
  if val>=7:ax.text(left+50*val/den,yy,str(val),ha='center',va='center',fontsize=8,color=ink if col==gray else 'white')
  elif val:ax.text(101,yy,str(val),ha='left',va='center',fontsize=8,color=rust)
  left+=100*val/den
 rows.append({'rule':rule,'csf_reference':cl,'correct_definitive':vals[0],'gray':vals[1],'discordant_definitive':vals[2],'denominator':den})
ax.set(yticks=[3.7,2.8,1.2,.3],yticklabels=['Empirical 90/90','Confidence 90/90','Empirical 90/90','Confidence 90/90'],xlim=(0,110),xticks=[0,25,50,75,100],ylim=(-.5,4.45),xlabel='Within CSF stratum (%)')
ax.text(0,4.23,'CSF positive (n = 99)',fontweight='bold',fontsize=8.5)
ax.text(0,1.75,'CSF negative (n = 77)',fontweight='bold',fontsize=8.5)
ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color=blue,label='Correct'),Patch(color=gray,label='Gray'),Patch(color=rust,label='Discordant')],ncol=3,loc='lower center',bbox_to_anchor=(.325,.015),fontsize=7.5,frameon=False,columnspacing=.8,handlelength=1)
fig.text(.028,.94,'a',fontweight='bold',fontsize=12)
ax=fig.add_subplot(gs[0,1]); fig.text(.597,.94,'b',fontweight='bold',fontsize=12)
# Labels occupy explicit free areas, away from points and all uncertainty bars.
label_artists=[];errorbar_artists=[];marker_positions=[]
for rule,label,col,marker,label_xy,alignment in [('empirical90','Empirical 90/90',blue,'o',(37,10.5),'left'),('empirical95','Empirical 95/95',blue,'s',(59.5,6.15),'left'),('assured90','Confidence\n90/90',green,'o',(65,3.7),'left'),('assured95','Confidence\n95/95',green,'s',(75,1.9),'center')]:
 m=R['crossfit'][rule]; xx=m['gray_fraction'];yy=m['residual_error_fraction'];x0=xx['mean']*100;y0=yy['mean']*100
 eb=ax.errorbar(x0,y0,xerr=np.array([[x0-xx['split_p2_5']*100],[xx['split_p97_5']*100-x0]]),yerr=np.array([[y0-yy['split_p2_5']*100],[yy['split_p97_5']*100-y0]]),fmt=marker,color=col,markersize=5,elinewidth=.9,capsize=2,zorder=3)
 errorbar_artists.append((rule,eb));marker_positions.append((rule,x0,y0))
 text=ax.text(*label_xy,label,ha=alignment,va='center',fontsize=8,color=col,zorder=5,bbox={'facecolor':'white','edgecolor':'none','pad':0.6})
 label_artists.append((rule,text))
ax.scatter([100],[0],marker='x',color='#899599',s=20,zorder=3)
label_artists.append(('confirm_all',ax.text(91,-.12,'Confirm all',ha='right',va='center',fontsize=7.5,color='#687782',zorder=5,bbox={'facecolor':'white','edgecolor':'none','pad':0.5})))
marker_positions.append(('confirm_all',100,0))
ax.set(xlim=(20,105),ylim=(-.7,14),xticks=[25,50,75,100],xlabel='Reference confirmation (%)',ylabel='Residual discordance (% of all rows)')
ax.grid(alpha=.2,axis='both',zorder=0)

# Audit text rectangles against every data marker, interval and cap in panel b.
# Grid lines and the intentional counts within the panel-a bars are excluded.
from matplotlib.transforms import Bbox
fig.canvas.draw();renderer=fig.canvas.get_renderer();padding=fig.dpi/72
text_boxes=[(name,text.get_bbox_patch().get_window_extent(renderer)) for name,text in label_artists]
data_boxes=[]
for rule,x,y in marker_positions:
 px,py=ax.transData.transform((x,y));rad=4*padding
 data_boxes.append((rule+' marker',Bbox.from_extents(px-rad,py-rad,px+rad,py+rad)))
for rule,eb in errorbar_artists:
 for j,cap in enumerate(eb.lines[1]):data_boxes.append((rule+' cap '+str(j),cap.get_window_extent(renderer)))
 for j,collection in enumerate(eb.lines[2]):
  for k,segment in enumerate(collection.get_segments()):
   points=ax.transData.transform(segment);lo=points.min(axis=0)-padding;hi=points.max(axis=0)+padding
   data_boxes.append((rule+' interval '+str(j)+'-'+str(k),Bbox.from_extents(lo[0],lo[1],hi[0],hi[1])))
collisions=[{'label':name,'data':data_name} for name,b in text_boxes for data_name,db in data_boxes if b.overlaps(db)]
label_collisions=[{'first':name,'second':other} for i,(name,b) in enumerate(text_boxes) for other,ob in text_boxes[i+1:] if b.overlaps(ob)]
axis_box=ax.get_window_extent(renderer)
outside=[name for name,b in text_boxes if b.x0<axis_box.x0 or b.x1>axis_box.x1 or b.y0<axis_box.y0 or b.y1>axis_box.y1]
audit={'date':'2026-10-20','scope':'Figure 1b text versus markers, uncertainty intervals, caps and other labels',
 'label_data_collisions':collisions,'label_label_collisions':label_collisions,'labels_outside_plot':outside,
 'label_rectangles_pixels':{name:list(b.extents) for name,b in text_boxes},
 'data_coordinates':marker_positions,'scientific_results_changed':False}
(ROOT/'qa').mkdir(exist_ok=True)
(ROOT/'qa/figure1_geometry_check.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
assert not collisions and not label_collisions and not outside,audit
finish(fig,'Figure_1')
pd.DataFrame(rows).to_csv(F/'Figure_1a_source_data.csv',index=False)
pd.DataFrame([{'rule':k,'confirmation_mean':v['gray_fraction']['mean'],'confirmation_p2_5':v['gray_fraction']['split_p2_5'],'confirmation_p97_5':v['gray_fraction']['split_p97_5'],'discordance_mean':v['residual_error_fraction']['mean'],'discordance_p2_5':v['residual_error_fraction']['split_p2_5'],'discordance_p97_5':v['residual_error_fraction']['split_p97_5']} for k,v in R['crossfit'].items() if k!='marginal90']).to_csv(F/'Figure_1b_source_data.csv',index=False)

if '--figure1-only' in sys.argv:
 print('Updated Figure 1 only; label geometry passed; source-data files regenerated without changing values.')
 sys.exit(0)

cv=pd.read_csv(ROOT/'results/crossfit_cutoffs.csv');fig,axs=plt.subplots(1,2,figsize=(7.35,3.2));fig.subplots_adjust(left=.19,right=.98,bottom=.2,top=.89,wspace=.52)
keys=['empirical90','assured90','empirical95','assured95'];labs=['Empirical 90/90','Confidence 90/90','Empirical 95/95','Confidence 95/95']
for j,(col,lab) in enumerate([('lower','Rule-out cutoff (pg/mL)'),('upper','Rule-in cutoff (pg/mL)')]):
 ax=axs[j]
 for i,k in enumerate(keys):
  v=pd.to_numeric(cv.loc[cv.rule==k,col]);v=v[np.isfinite(v)]
  if len(v):
   q=np.quantile(v,[.025,.5,.975]);ax.errorbar(q[1],3-i,xerr=[[q[1]-q[0]],[q[2]-q[1]]],fmt='o',color=green if 'assured' in k else blue,capsize=3,markersize=5)
  else:ax.text(.027,3-i,'No finite cutoff',va='center',ha='center',fontsize=8,color=rust)
 ax.set(yticks=range(4),yticklabels=labs[::-1] if j==0 else [],ylim=(-.5,3.5),xlabel=lab)
 ax.grid(axis='x',alpha=.15);ax.text(-.51 if j==0 else -.16,1.05,chr(97+j),transform=ax.transAxes,fontweight='bold',fontsize=12)
 if j==0:ax.set_xlim(0,.014);ax.set_xticks([0,.004,.008,.012]);ax.set_xticklabels(['0.000','0.004','0.008','0.012'])
 else:ax.set_xlim(.012,.047)
finish(fig,'Supplementary_Figure_1')

prev=pd.read_csv(ROOT/'results/prevalence_sensitivity.csv');fig,axs=plt.subplots(1,2,figsize=(7.35,3.2));fig.subplots_adjust(left=.095,right=.98,bottom=.23,top=.91,wspace=.34)
for k,lab,col,ls in [('empirical90','Empirical 90/90',blue,'-'),('assured90','Confidence 90/90',green,'--')]:
 dd=prev[prev.rule==k]
 axs[0].plot(dd.prevalence*100,dd.gray_confirmation*100,color=col,ls=ls,marker='o',markersize=4,label=lab)
 axs[1].plot(dd.prevalence*100,dd.negative_residual_risk*100,color=col,ls=ls,marker='o',markersize=4,label=lab)
for j,ax in enumerate(axs):
 ax.set(xlabel='Assumed CSF positivity (%)',xlim=(7,60),xticks=[10,30,50]);ax.grid(alpha=.15)
 ax.text(-.19,1.05,chr(97+j),transform=ax.transAxes,fontweight='bold',fontsize=12)
axs[0].set(ylabel='Gray-zone confirmation (%)',ylim=(20,70));axs[1].set(ylabel='CSF positivity after rule-out (%)',ylim=(0,20));axs[1].legend(frameon=False,fontsize=7.5)
finish(fig,'Supplementary_Figure_2')
print('Created Figure 1 and Supplementary Figures 1-2 in SVG/PDF/PNG/JPEG/TIFF; data-driven only.')
