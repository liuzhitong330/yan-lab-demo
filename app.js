(function () {
  'use strict';
  function mean(a) { return a.length ? a.reduce((s,v)=>s+v,0)/a.length : null; }
  function sd(a) { const m=mean(a); return a.length>1 ? Math.sqrt(a.reduce((s,v)=>s+(v-m)**2,0)/(a.length-1)) : null; }
  function regression(frames) {
    const f=frames.filter(v=>v.center_valid && Number.isFinite(v.center_um));
    if(f.length<3) return {n:f.length,slope:null,intercept:null,r2:null};
    const mx=mean(f.map(v=>v.time_s)), my=mean(f.map(v=>v.center_um));
    const xx=f.reduce((s,v)=>s+(v.time_s-mx)**2,0), yy=f.reduce((s,v)=>s+(v.center_um-my)**2,0);
    const xy=f.reduce((s,v)=>s+(v.time_s-mx)*(v.center_um-my),0);
    return {n:f.length,slope:xy/xx,intercept:my-xy/xx*mx,r2:yy ? xy*xy/xx/yy : 0};
  }
  function gaussian(x,p) { return p[0]*Math.exp(-((x-p[2])**2)/(2*p[1]**2))+p[3]; }
  function flag(c,t) { return c.shift_pp===null?'Missing context':Math.abs(c.shift_pp)>t?'Review baseline':'Within tolerance'; }
  function csv(rows) { return rows.map(row=>row.map(v=>'"'+String(v??'').replaceAll('"','""')+'"').join(',')).join('\r\n'); }
  if(typeof module!=='undefined') { module.exports={mean,sd,regression,gaussian,flag,csv}; return; }
  const $=id=>document.getElementById(id), fmt=(v,n=2)=>v===null||!Number.isFinite(v)?'not available':v.toFixed(n);
  const sign=v=>(v>=0?'+':'')+fmt(v), ns='http://www.w3.org/2000/svg';
  const colors=['#1f7a8c','#666','#c07a2a'];
  function el(svg,tag,attrs,text) { const n=document.createElementNS(ns,tag); Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v)); if(text!==undefined)n.textContent=text;svg.appendChild(n);return n; }
  function axes(svg,{xmin,xmax,ymin,ymax,height=285,xlabel,ylabel}) {
    svg.replaceChildren(); const left=58,right=584,top=26,bottom=height-53;
    const x=v=>left+(v-xmin)/(xmax-xmin)*(right-left), y=v=>bottom-(v-ymin)/(ymax-ymin)*(bottom-top);
    for(let i=0;i<=4;i++){const v=ymin+(ymax-ymin)*i/4;el(svg,'line',{x1:left,y1:y(v),x2:right,y2:y(v),stroke:'#e4e4e4'});el(svg,'text',{x:left-8,y:y(v)+4,'text-anchor':'end','font-size':11},fmt(v,1));}
    if(xlabel){for(let i=0;i<=4;i++){const v=xmin+(xmax-xmin)*i/4;el(svg,'text',{x:x(v),y:bottom+20,'text-anchor':'middle','font-size':11},fmt(v,0));}el(svg,'text',{x:320,y:height-7,'text-anchor':'middle','font-size':12},xlabel);}
    el(svg,'text',{x:left,y:14,'font-size':12},ylabel);return{x,y,left,right,top,bottom};
  }
  function download(name,content,type='text/csv') { const u=URL.createObjectURL(new Blob([content],{type})),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1500); }
  window.YAN_DATA_READY.then(({primary,secondary})=>{
    const constructs=primary.constructs,paired=constructs.filter(c=>c.shift_pp!==null);
    constructs.forEach(c=>{const o=document.createElement('option');o.value=c.id;o.textContent=c.id+' · '+c.repeat_count+' repeats';$('construct').appendChild(o);});
    $('construct').value='GPGGA-30';
    ['GPGGA-30','GGSGGS-30','GPGGA-10'].forEach(id=>{const b=document.createElement('button');b.textContent=id;b.onclick=()=>{$('construct').value=id;renderPrimary();};$('suggestions').appendChild(b);});
    function current(){return constructs.find(c=>c.id===$('construct').value);}
    function renderPrimary(){
      const c=current(),t=Number($('tolerance').value),svg=$('hero-viz');
      $('tolerance-value').textContent=t.toFixed(1);
      const {x,y,bottom}=axes(svg,{xmin:0,xmax:3,ymin:0,ymax:100,ylabel:'Unloaded FRET efficiency (%)'});
      ['vitro','cell'].forEach((key,j)=>{
        const vals=c[key],cx=x(j+1),col=j?'#1f7a8c':'#888';
        vals.forEach((v,i)=>el(svg,'circle',{cx:cx+(((i*37)%101)/100-.5)*75,cy:y(v),r:2.6,fill:col,opacity:.55}));
        if(vals.length){const m=mean(vals),s=sd(vals);el(svg,'line',{x1:cx,y1:y(m-s),x2:cx,y2:y(m+s),stroke:'#222','stroke-width':2});[m-s,m+s].forEach(v=>el(svg,'line',{x1:cx-8,y1:y(v),x2:cx+8,y2:y(v),stroke:'#222','stroke-width':2}));el(svg,'line',{x1:cx-15,y1:y(m),x2:cx+15,y2:y(m),stroke:'#222','stroke-width':3});}
        else el(svg,'text',{x:cx,y:y(50),'text-anchor':'middle','font-size':13},'Not measured');
        el(svg,'text',{x:cx,y:bottom+22,'text-anchor':'middle','font-size':13},j?'In cells':'Lysate');
        el(svg,'text',{x:cx,y:bottom+41,'text-anchor':'middle','font-size':11},'n = '+vals.length+(j?' cells':' experiments'));
      });
      $('readout').textContent=c.id+': lysate '+(c.vitro.length?fmt(mean(c.vitro))+'%':'not measured')+'; cells '+(c.cell.length?fmt(mean(c.cell))+'%':'not measured')+'. '+(c.shift_pp===null?'The cross-context shift is unavailable; no value is imputed.': 'Cell minus lysate: '+sign(c.shift_pp)+' percentage points. '+flag(c,t)+'.');
      $('metric-one').textContent=constructs.length;$('metric-two').textContent=paired.length;$('metric-three').textContent=paired.filter(c=>Math.abs(c.shift_pp)>t).length+'/'+paired.length;
      $('review-summary').textContent='Review all 16 constructs at the '+t.toFixed(1)+' pp planning tolerance';
      $('construct-table').replaceChildren();
      constructs.forEach(c=>{const r=document.createElement('tr');[c.id,c.vitro.length,c.cell.length,c.shift_pp===null?'—':sign(c.shift_pp),flag(c,t)].forEach(v=>{const td=document.createElement('td');td.textContent=v;r.appendChild(td);});$('construct-table').appendChild(r);});
      $('plan-readout').textContent='Proposed panel: '+c.id+' as the selected public benchmark, plus the matched-length GPGGA-30 / GGSGGS-30 comparison and GPGGA-10 as a low-shift contrast. Re-test unloaded baselines in the same intended host, batch structure and acquisition setting. This is a candidate/control rationale; no full plasmid design or force-response validation is completed.';
    }
    function state(){const movie=secondary.movies.find(m=>m.id===$('movie').value),n=$('window').value==='common'?22:movie.author_fit_frames;return{movie,n,radius:Number($('radius').value)};}
    function renderMotion(){
      const {movie,n,radius}=state(),svg=$('motion-viz');
      const traces=movie.variants.map(v=>{const f=v.frames.slice(0,n),ret=f.filter(f=>f.center_valid),base=ret.length?ret[0].center_um:0;return{v,f,ret,base,fit:regression(f)};});
      const values=traces.flatMap(t=>t.ret.map(f=>f.center_um-t.base));const lo=Math.min(-.5,...values),hi=Math.max(.5,...values),pad=(hi-lo)*.12;
      const {x,y}=axes(svg,{xmin:0,xmax:(n-1)*movie.frame_interval_s,ymin:lo-pad,ymax:hi+pad,height:330,xlabel:'Seconds from first analyzed frame',ylabel:'Approx. peak displacement (µm)'});
      traces.forEach((t,j)=>{const col=colors[j],width=t.v.erosion_radius_px===radius?2:1;
        // Gaps remain gaps: points, not interpolated trajectories.
        t.ret.forEach(f=>el(svg,'circle',{cx:x(f.time_s),cy:y(f.center_um-t.base),r:width+1.4,fill:col,opacity:.8}));
        if(t.fit.slope!==null){const first=t.ret[0].time_s,last=t.ret[t.ret.length-1].time_s;el(svg,'line',{x1:x(first),y1:y(t.fit.intercept+t.fit.slope*first-t.base),x2:x(last),y2:y(t.fit.intercept+t.fit.slope*last-t.base),stroke:col,'stroke-dasharray':'5 4','stroke-width':width});}
      });
      $('motion-table').replaceChildren();traces.forEach(t=>{const tr=document.createElement('tr');[t.v.erosion_radius_px+(t.v.erosion_radius_px===movie.original_erosion_radius_px?' (author)':''),fmt(t.fit.slope===null?null:t.fit.slope*1000),t.fit.n+'/'+n,fmt(t.fit.r2,3)].forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.appendChild(td);});$('motion-table').appendChild(tr);});
      const chosen=traces.find(t=>t.v.erosion_radius_px===radius),failed=chosen.f.filter(f=>f.fit_failed).length,warn=chosen.f.filter(f=>!f.fit_failed&&f.fit_warning.length).length;
      $('motion-readout').textContent=movie.label+' · '+radius+' px · '+n+' frame positions: '+fmt(chosen.fit.slope===null?null:chosen.fit.slope*1000)+' approximate nm/s, '+chosen.fit.n+' retained; '+(n-chosen.fit.n)+' excluded by fit failure or author center gate. '+failed+' failed fits; '+warn+' covariance warnings. Retention alone does not establish fit quality.';
      $('frame').max=n;if(Number($('frame').value)>n)$('frame').value=n;renderProfile();
    }
    function renderProfile(){
      const {movie,radius}=state(),v=movie.variants.find(v=>v.erosion_radius_px===radius),f=v.frames[Number($('frame').value)-1];$('frame-value').textContent=f.frame_index;
      const scale=(Math.SQRT2*.1+.1)/2,pred=f.gaussian_parameters&&f.gaussian_parameters.every(Number.isFinite)?v.x_um.map(x=>gaussian(x/scale,f.gaussian_parameters)):null;
      const all=f.observed.concat(pred||[]),min=Math.min(0,...all),max=Math.max(...all)*1.08;
      const {x,y}=axes($('profile-viz'),{xmin:v.x_um[0],xmax:v.x_um[v.x_um.length-1],ymin:min,ymax:max,height:260,xlabel:'Approx. unrolled coordinate (µm)',ylabel:'CellMask intensity (a.u.)'});
      [f.observed,pred].forEach((a,j)=>{if(a)el($('profile-viz'),'path',{d:a.map((p,i)=>(i?'L':'M')+x(v.x_um[i])+','+y(p)).join(' '),fill:'none',stroke:j?'#c07a2a':'#1f7a8c','stroke-width':j?2:1.3});});
      $('profile-readout').textContent='Teal: observed; orange: Gaussian fit. '+(f.fit_failed?'Fit did not converge; excluded from regression.':f.center_valid?'Retained by the author center gate.':'Excluded by the author center gate.')+' Normalized RMSE: '+fmt(f.fit_nrmse,3)+'. '+(f.fit_warning.length?'Diagnostic: '+f.fit_warning.join('; '):'No recorded covariance warning.')+' This status is not a biological quality label.';
    }
    $('construct').onchange=renderPrimary;$('tolerance').oninput=renderPrimary;
    ['movie','window','radius'].forEach(id=>$(id).onchange=renderMotion);$('frame').oninput=renderProfile;
    $('export-constructs').onclick=()=>{const t=+$('tolerance').value;download('yan-construct-comparison.csv',csv([['construct','lysate_n_experiments','cell_n_pooled_cells','lysate_mean_fret_pct','cell_mean_fret_pct','cell_minus_lysate_pp','planning_tolerance_pp','planning_flag','caution'],...constructs.map(c=>[c.id,c.vitro.length,c.cell.length,mean(c.vitro),mean(c.cell),c.shift_pp,t,flag(c,t),'Unpaired descriptive benchmark; host and modality confounded; not force calibration'])]));};
    $('export-plan').onclick=()=>{const c=current();download('yan-next-test-record.json',JSON.stringify({selected_public_benchmark:c.id,nominal_repeat_segment:c.repeat_segment,not_full_insert_sequence:true,source:primary.source,observed_shift_pp:c.shift_pp,planning_tolerance_pp:+$('tolerance').value,comparison_panel:[...new Set([c.id,'GPGGA-30','GGSGGS-30','GPGGA-10'])],status:'PROPOSED; NOT PERFORMED',required_checks:['Verify full construct/plasmid sequence and junctions','Use matched host, targeting and acquisition settings','Record independently cultured biological batch and cell identifiers','Donor-only, acceptor-only and unloaded/force-insensitive controls','Check expression, localization and cell health','Direct force–fluorescence calibration with loading/unloading','Review blinded segmentation and parameter sensitivity'],limits:'Public external unloaded-FRET benchmark; no force range inferred; no new experiment performed'},null,2),'application/json');};
    $('export-motion').onclick=()=>{const {movie,n,radius}=state(),v=movie.variants.find(v=>v.erosion_radius_px===radius);download('yan-'+movie.id+'-r'+radius+'-frames.csv',csv([['movie','radius_px','source_frame','time_from_first_analyzed_s','center_um_approx','retained_by_author_center_gate','fit_failed','fit_warning','fit_nrmse','window_frame_positions'],...v.frames.slice(0,n).map(f=>[movie.id,radius,f.frame_index,f.time_s,f.center_um,f.center_valid,f.fit_failed,f.fit_warning.join('; '),f.fit_nrmse,n])]));};
    renderPrimary();renderMotion();
  }).catch(err=>{$('readout').textContent='Data could not be loaded. Please reload this page or consult the downloadable source files. '+err.message;});
})();
