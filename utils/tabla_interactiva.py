import json
import numpy as _np
import streamlit.components.v1 as components


def _serial(obj):
    if isinstance(obj, _np.bool_):    return bool(obj)
    if isinstance(obj, _np.integer):  return int(obj)
    if isinstance(obj, _np.floating): return None if _np.isnan(obj) else float(obj)
    if isinstance(obj, float) and obj != obj: return None
    import pandas as _pd
    try:
        if _pd.isna(obj): return None
    except (TypeError, ValueError):
        pass
    if hasattr(obj, 'strftime'):
        return obj.strftime('%Y-%m-%d')
    raise TypeError(repr(obj))


_TABLE_TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#ffffff;--bg2:#f4f6fa;--bg3:#eaecf4;
  --brd:#cfd4e0;--brd2:#e2e6f0;
  --txt:#1a1d2e;--txt2:#4a5068;--txt3:#8892a8;
  --hov:#e8ecf6;--acc:#FF4B4B;--shd:rgba(0,0,0,0.13);
  --ok:#16a34a;--no:#dc2626;
  --bc-bg:#f0fdf4;--bc-txt:#15803d;--bc-brd:#86efac;
  --bi-bg:#fef2f2;--bi-txt:#dc2626;--bi-brd:#fca5a5;
}
@media(prefers-color-scheme:dark){:root{
  --bg:#0e1117;--bg2:#181b26;--bg3:#12151f;
  --brd:#2a2f42;--brd2:#222636;
  --txt:#e8ecfa;--txt2:#8892b4;--txt3:#4e566e;
  --hov:#1e2235;--acc:#FF6B6B;--shd:rgba(0,0,0,0.5);
  --ok:#4ade80;--no:#f87171;
  --bc-bg:#052e16;--bc-txt:#4ade80;--bc-brd:#166534;
  --bi-bg:#450a0a;--bi-txt:#f87171;--bi-brd:#991b1b;
}}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:transparent}
body{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:13px;color:var(--txt)}
#toolbar{display:flex;justify-content:flex-end;align-items:center;padding:4px 0 8px;gap:10px;font-size:12px;color:var(--txt2)}
#ps{padding:3px 8px;border:1px solid var(--brd);border-radius:4px;font-size:12px;cursor:pointer;background:var(--bg);color:var(--txt)}
.tw{overflow-x:auto;overflow-y:auto;max-height:__MAXH__px;border:1px solid var(--brd);border-radius:6px 6px 0 0;background:var(--bg)}
table{width:100%;border-collapse:collapse}
thead{position:sticky;top:0;z-index:20}
th{background:var(--bg2);border-bottom:1px solid var(--brd);border-right:1px solid var(--brd2);padding:0;position:relative;user-select:none;white-space:nowrap}
.chi{display:flex;align-items:center;padding:8px 10px;cursor:pointer;gap:4px}
.chi:hover{background:var(--hov)}
.cn{flex:1;font-weight:700;font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--txt2);overflow:hidden;text-overflow:ellipsis}
.sa{font-size:10px;color:var(--acc);min-width:12px;flex-shrink:0;font-weight:700}
.rh{position:absolute;right:0;top:0;bottom:0;width:5px;cursor:col-resize;z-index:1}
.rh:hover,.rh.active{background:rgba(255,75,75,.35)}
.fc{background:var(--bg3);border-bottom:2px solid var(--brd);border-right:1px solid var(--brd2);padding:3px 4px}
.ft{display:flex;align-items:center;justify-content:space-between;width:100%;padding:4px 7px;border:1px solid var(--brd);border-radius:3px;font-size:11px;background:var(--bg);color:var(--txt);cursor:pointer;white-space:nowrap;overflow:hidden;gap:4px;line-height:1.4}
.ft:hover{border-color:var(--acc)}
.ft.on{border-color:var(--acc);font-weight:600;color:var(--acc)}
.ft-l{flex:1;overflow:hidden;text-overflow:ellipsis;text-align:left}
.ft-c{flex-shrink:0;font-size:9px;color:var(--txt3)}
td{padding:7px 10px;border-bottom:1px solid var(--brd2);border-right:1px solid var(--brd2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:13px;color:var(--txt);max-width:220px}
tr:hover td{background:var(--hov)}
.bt{text-align:center;color:var(--ok);font-size:15px;font-weight:700}
.bf{text-align:center;color:var(--no);font-size:15px;font-weight:700}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700;letter-spacing:.3px}
.bc{background:var(--bc-bg);color:var(--bc-txt);border:1px solid var(--bc-brd)}
.bi{background:var(--bi-bg);color:var(--bi-txt);border:1px solid var(--bi-brd)}
#pb{display:flex;align-items:center;justify-content:center;gap:8px;padding:8px 0;border:1px solid var(--brd);border-top:none;border-radius:0 0 6px 6px;background:var(--bg2)}
#pb button{padding:4px 12px;border:1px solid var(--brd);border-radius:4px;background:var(--bg);cursor:pointer;font-size:12px;color:var(--txt);white-space:nowrap}
#pb button:hover:not(:disabled){background:var(--hov);border-color:var(--acc)}
#pb button:disabled{opacity:.3;cursor:not-allowed}
#pi{min-width:270px;text-align:center;font-size:12px;font-weight:500;color:var(--txt2)}
.nr td{color:var(--txt3);text-align:center;padding:28px;font-style:italic}
.dp-panel{position:fixed;z-index:9999;background:var(--bg);border:1px solid var(--brd);border-radius:6px;box-shadow:0 8px 24px var(--shd);min-width:160px;max-height:270px;display:flex;flex-direction:column;overflow:hidden}
.dp-search{padding:6px 8px;border-bottom:1px solid var(--brd);flex-shrink:0}
.dp-search input{width:100%;padding:4px 7px;border:1px solid var(--brd);border-radius:3px;font-size:11px;background:var(--bg);color:var(--txt);outline:none}
.dp-search input:focus{border-color:var(--acc)}
.dp-list{overflow-y:auto;flex:1}
.dp-opt{display:flex;align-items:center;gap:7px;padding:6px 10px;cursor:pointer;font-size:12px;color:var(--txt)}
.dp-opt:hover{background:var(--hov)}
.dp-opt.sel{background:var(--hov)}
.dp-cb{width:14px;height:14px;border:1.5px solid var(--brd);border-radius:3px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:10px;color:var(--bg);background:var(--bg);transition:all .1s}
.dp-opt.sel .dp-cb{background:var(--acc);border-color:var(--acc)}
.dp-clr{font-size:11px;color:var(--txt3);padding:5px 10px;border-bottom:1px solid var(--brd);flex-shrink:0;cursor:pointer}
.dp-clr:hover{color:var(--acc);background:var(--hov)}
.tw::-webkit-scrollbar{width:5px;height:5px}
.tw::-webkit-scrollbar-track{background:transparent}
.tw::-webkit-scrollbar-thumb{background:var(--brd);border-radius:3px}
.tw::-webkit-scrollbar-thumb:hover{background:var(--txt3)}
.tw::-webkit-scrollbar-corner{background:transparent}
</style></head>
<body>
<div id="toolbar">
  <label>Filas por página:&nbsp;<select id="ps">
    <option value="10" selected>10</option>
    <option value="15">15</option>
    <option value="25">25</option>
    <option value="50">50</option>
  </select></label>
</div>
<div class="tw" id="tw">
  <table><thead id="thead"></thead><tbody id="tbody"></tbody></table>
</div>
<div id="pb">
  <button id="b0">&#171;</button>
  <button id="bp">&#8592; Anterior</button>
  <span id="pi"></span>
  <button id="bn">Siguiente &#8594;</button>
  <button id="bl">&#187;</button>
</div>
<script>
const DATA=__DATA__;
const COLS=__COLUMNS__;
const BCOLS=new Set(__BOOL_COLS__);
const BADGE_COLS=__BADGE_COLS__;
const CW=(()=>{const w={};COLS.forEach(c=>{w[c]=BCOLS.has(c)?68:120});return w;})();

const UV=(()=>{
  const u={};
  COLS.forEach(c=>{
    if(BCOLS.has(c)){u[c]=[{v:"true",l:"Entregado"},{v:"false",l:"Faltante"}];}
    else{
      const s=new Set(DATA.map(r=>r[c]).filter(x=>x!=null&&x!==""));
      u[c]=[...s].sort((a,b)=>String(a).localeCompare(String(b),"es")).map(v=>({v:String(v),l:String(v)}));
    }
  });
  return u;
})();

let S={flt:Object.fromEntries(COLS.map(c=>[c,[]])),sc:null,sd:1,pg:0,ps:10};
let _ac=null,_at=null,_panel=null;

function filt(){
  let r=DATA;
  for(const c of COLS){
    const sel=S.flt[c];if(!sel.length)continue;
    r=r.filter(x=>sel.includes(String(x[c])));
  }
  return r;
}

function srt(data){
  if(!S.sc)return data;
  const c=S.sc,d=S.sd;
  return[...data].sort((a,b)=>{
    let va=a[c]??"",vb=b[c]??"";
    if(typeof va==="boolean")va=va?1:0;if(typeof vb==="boolean")vb=vb?1:0;
    if(typeof va==="string")va=va.toLowerCase();if(typeof vb==="string")vb=vb.toLowerCase();
    return va<vb?-d:va>vb?d:0;
  });
}

function trigLabel(col){
  const sel=S.flt[col];
  if(!sel.length)return"Todos";
  if(sel.length===1){const o=UV[col].find(x=>x.v===sel[0]);return o?o.l:sel[0];}
  return`${sel.length} seleccionados`;
}

function updTrig(col,el){
  el.querySelector(".ft-l").textContent=trigLabel(col);
  el.classList.toggle("on",S.flt[col].length>0);
}

function render(){
  const f=srt(filt()),n=f.length;
  const tp=Math.max(1,Math.ceil(n/S.ps));
  S.pg=Math.min(Math.max(0,S.pg),tp-1);
  const s=S.pg*S.ps,e=Math.min(s+S.ps,n);
  const tb=document.getElementById("tbody");
  tb.innerHTML="";
  if(!n){
    const tr=tb.insertRow();tr.className="nr";
    const td=tr.insertCell();td.colSpan=COLS.length;td.textContent="Sin resultados con los filtros aplicados.";
  }else{
    for(const row of f.slice(s,e)){
      const tr=tb.insertRow();
      for(const col of COLS){
        const td=tr.insertCell();const v=row[col];
        if(BCOLS.has(col)){td.className=v===true?"bt":"bf";td.textContent=v===true?"✓":"✗";}
        else if(BADGE_COLS[col]){
          const cls=BADGE_COLS[col][v]||"";
          if(cls){const sp=document.createElement("span");sp.className="badge "+cls;sp.textContent=v??"";td.appendChild(sp);}
          else{td.textContent=v??"—";if(v)td.title=v;}
        }
        else{td.textContent=v??"—";if(v)td.title=v;}
      }
    }
  }
  document.getElementById("pi").textContent=n?`${s+1}–${e} de ${n} registros · Página ${S.pg+1}/${tp}`:"Sin resultados";
  ["b0","bp"].forEach(id=>document.getElementById(id).disabled=S.pg===0);
  ["bn","bl"].forEach(id=>document.getElementById(id).disabled=S.pg>=tp-1);
  document.querySelectorAll(".sa").forEach((el,i)=>{el.textContent=COLS[i]===S.sc?(S.sd===1?" ↑":" ↓"):"";});
}

function hideDrop(){if(_panel){_panel.remove();_panel=null;}_ac=null;_at=null;}

function showDrop(col,trigEl){
  if(_ac===col){hideDrop();return;}
  hideDrop();_ac=col;_at=trigEl;
  const opts=UV[col];
  const panel=document.createElement("div");panel.className="dp-panel";

  let si=null;
  if(opts.length>8){
    const ds=document.createElement("div");ds.className="dp-search";
    si=document.createElement("input");si.type="text";si.placeholder="Buscar...";
    ds.appendChild(si);panel.appendChild(ds);
  }

  const dc=document.createElement("div");dc.className="dp-clr";dc.textContent="Limpiar filtro";
  dc.onclick=e=>{e.stopPropagation();S.flt[col]=[];S.pg=0;render();updTrig(col,trigEl);hideDrop();};
  panel.appendChild(dc);

  const list=document.createElement("div");list.className="dp-list";

  function buildList(term){
    list.innerHTML="";
    const lo=term?term.toLowerCase():"";
    for(const opt of opts){
      if(lo&&!opt.l.toLowerCase().includes(lo))continue;
      const isSel=S.flt[col].includes(opt.v);
      const d=document.createElement("div");d.className="dp-opt"+(isSel?" sel":"");
      const cb=document.createElement("span");cb.className="dp-cb";cb.textContent=isSel?"✓":"";
      const lb=document.createElement("span");lb.textContent=opt.l;
      d.append(cb,lb);
      d.onclick=e=>{
        e.stopPropagation();
        const idx=S.flt[col].indexOf(opt.v);
        if(idx>=0)S.flt[col].splice(idx,1);else S.flt[col].push(opt.v);
        S.pg=0;render();updTrig(col,trigEl);buildList(si?si.value:"");
      };
      list.appendChild(d);
    }
  }
  buildList("");
  if(si)si.oninput=()=>buildList(si.value);
  panel.appendChild(list);
  _panel=panel;
  document.body.appendChild(panel);

  const r=trigEl.getBoundingClientRect();
  panel.style.top=(r.bottom+2)+"px";
  panel.style.left=r.left+"px";
  panel.style.minWidth=Math.max(160,r.width)+"px";
  if(si)setTimeout(()=>si.focus(),0);
}

document.addEventListener("click",e=>{
  if(!e.target.closest(".dp-panel")&&!e.target.closest(".ft"))hideDrop();
});
document.getElementById("tw").addEventListener("scroll",hideDrop);

function startResize(th,e){
  e.preventDefault();e.stopPropagation();
  const h=e.currentTarget;h.classList.add("active");
  const x0=e.clientX,w0=th.getBoundingClientRect().width;
  const mm=e2=>{const w=Math.max(50,w0+e2.clientX-x0)+"px";th.style.width=th.style.minWidth=w;};
  const mu=()=>{h.classList.remove("active");document.removeEventListener("mousemove",mm);document.removeEventListener("mouseup",mu);};
  document.addEventListener("mousemove",mm);document.addEventListener("mouseup",mu);
}

function init(){
  const thead=document.getElementById("thead");

  const hr=document.createElement("tr");
  COLS.forEach(col=>{
    const th=document.createElement("th");th.style.width=th.style.minWidth=CW[col]+"px";
    const inner=document.createElement("div");inner.className="chi";
    inner.onclick=()=>{S.sd=S.sc===col?S.sd*-1:1;S.sc=col;render();};
    const nm=document.createElement("span");nm.className="cn";nm.textContent=col;
    const ar=document.createElement("span");ar.className="sa";
    const rh=document.createElement("div");rh.className="rh";
    rh.addEventListener("mousedown",e=>startResize(th,e));
    inner.append(nm,ar);th.append(inner,rh);hr.appendChild(th);
  });
  thead.appendChild(hr);

  const fr=document.createElement("tr");
  COLS.forEach(col=>{
    const th=document.createElement("th");th.className="fc";
    const btn=document.createElement("button");btn.className="ft";btn.type="button";
    const lbl=document.createElement("span");lbl.className="ft-l";lbl.textContent="Todos";
    const caret=document.createElement("span");caret.className="ft-c";caret.textContent="▾";
    btn.append(lbl,caret);
    btn.onclick=e=>{e.stopPropagation();showDrop(col,btn);};
    th.appendChild(btn);fr.appendChild(th);
  });
  thead.appendChild(fr);

  document.getElementById("b0").onclick=()=>{S.pg=0;render();};
  document.getElementById("bp").onclick=()=>{S.pg>0&&(S.pg--,render());};
  document.getElementById("bn").onclick=()=>{const tp=Math.max(1,Math.ceil(filt().length/S.ps));S.pg<tp-1&&(S.pg++,render());};
  document.getElementById("bl").onclick=()=>{S.pg=Math.max(0,Math.ceil(filt().length/S.ps)-1);render();};
  document.getElementById("ps").onchange=e=>{S.ps=parseInt(e.target.value);S.pg=0;render();};
  render();
}
document.addEventListener("DOMContentLoaded",init);
</script>
</body>
</html>"""


_PAGE_SIZE = 10   # debe coincidir con la opción selected del <select id="ps">
_ROW_H     = 37   # px por fila de datos (padding 7+7 + contenido)
_CHROME_H  = 182  # toolbar + encabezado col + fila filtros + barra paginación + bordes


def render_interactive_table(df, bool_cols=[], badge_cols={}, columns=None, height=500):
    """Renderiza una tabla HTML/CSS/JS interactiva en Streamlit.

    Parameters
    ----------
    df         : pd.DataFrame
    bool_cols  : list[str]       columnas booleanas → ✓/✗
    badge_cols : dict[str,dict]  {nombre_col: {valor: clase_css}}
                                 clases disponibles: "bc" (verde), "bi" (rojo)
    columns    : list[str]|None  columnas a mostrar en ese orden; None = todas
    height     : int|None        altura del iframe en píxeles;
                                 None = auto calculado según número de filas
    """
    if columns is not None:
        df = df[[c for c in columns if c in df.columns]].copy()

    if height is None:
        n_visible = min(max(len(df), 1), _PAGE_SIZE)
        height    = max(200, min(600, _CHROME_H + n_visible * _ROW_H))

    table_max_h   = max(150, height - 80)
    records       = df.to_dict(orient='records')
    cols          = list(df.columns)
    data_js       = json.dumps(records,         default=_serial, ensure_ascii=False)
    columns_js    = json.dumps(cols,            ensure_ascii=False)
    bool_cols_js  = json.dumps(list(bool_cols), ensure_ascii=False)
    badge_cols_js = json.dumps(badge_cols,      ensure_ascii=False)

    html = (_TABLE_TEMPLATE
            .replace("__DATA__",       data_js)
            .replace("__COLUMNS__",    columns_js)
            .replace("__BOOL_COLS__",  bool_cols_js)
            .replace("__BADGE_COLS__", badge_cols_js)
            .replace("__MAXH__",       str(table_max_h)))

    components.html(html, height=height, scrolling=False)
