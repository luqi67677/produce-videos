'use strict';

// 固定原图，仅合成已授权的嘴/眼局部。真实声音与轨迹来自同一整轨。
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawn, spawnSync} = require('node:child_process');
function args(argv) {
  const result = {};
  for (let i=0; i<argv.length; i+=2) {
    if (!argv[i].startsWith('--') || argv[i+1]===undefined) throw new Error('参数须成对提供');
    result[argv[i].slice(2)] = argv[i+1];
  }
  return result;
}
const opt = args(process.argv.slice(2));
for (const key of ['profile','motion','output']) if (!opt[key]) throw new Error(`缺少 --${key}`);
if (!/\.mp4$/i.test(opt.output)) throw new Error('--output 必须使用 .mp4 扩展名，避免审计文件覆盖视频');
const {createCanvas,loadImage} = require(opt['canvas-module'] || '@napi-rs/canvas');
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const bounded = n => Math.max(0,Math.min(1,n));

async function main() {
  const profilePath = path.resolve(opt.profile);
  const root = path.dirname(profilePath);
  const profile = JSON.parse(fs.readFileSync(profilePath,'utf8'));
  const motionPath = path.resolve(opt.motion);
  const motion = JSON.parse(fs.readFileSync(motionPath,'utf8'));
  const presentation = profile.presentation;
  if (presentation.mode !== 'audio-driven-presenter' || presentation.body_motion !== 'fixed' || presentation.mouth_driver !== 'amplitude') throw new Error('本渲染器仅接受固定身体的音量开合模式');
  if (motion.phoneme_level_lip_sync !== false || motion.body_motion !== 'fixed') throw new Error('运动轨迹声明不匹配');
  if (!presentation.animation_authorization) throw new Error('缺少口眼动画授权');
  const anchor = profile.reference_assets.find(a=>a.role==='identity-anchor');
  const originalPath = path.resolve(root,anchor.path);
  if (hash(originalPath)!==anchor.sha256) throw new Error('身份锚点已改变');
  if (hash(motion.source_audio_path)!==motion.source_audio_sha256) throw new Error('配音文件已改变');
  const sourceRefs = presentation.source_refs;
  const sourceByRegion = {};
  for (const ref of sourceRefs) {
    const p = path.resolve(root,ref.path);
    if (hash(p)!==ref.sha256) throw new Error(`局部素材已改变：${ref.region}`);
    sourceByRegion[ref.region] = await loadImage(p);
  }
  if (!sourceByRegion.mouth || !sourceByRegion.eyes) throw new Error('缺少嘴部或眼部素材');
  const original = await loadImage(originalPath);
  const local = presentation.local_composite;
  if (original.width!==local.source_dimensions[0] || original.height!==local.source_dimensions[1]) throw new Error('原图尺寸不匹配');
  const mouthROI=local.mouth_roi, eyeROIs=local.eye_rois;
  const rois=[mouthROI,...eyeROIs];
  for (const roi of rois) {
    const [x,y,w,h]=roi;
    if (![x,y,w,h].every(Number.isFinite) || x<0 || y<0 || w<=0 || h<=0 || x+w>original.width || y+h>original.height) throw new Error('局部矩形超出原图');
  }
  const base=createCanvas(original.width,original.height);
  const bctx=base.getContext('2d');
  bctx.drawImage(original,0,0);
  const baseData=bctx.getImageData(0,0,base.width,base.height).data;
  function patch(image,roi) {
    const [x,y,w,h]=roi;
    if (image.width!==original.width || image.height!==original.height) throw new Error('局部源图尺寸不匹配');
    const c=createCanvas(w,h),ctx=c.getContext('2d');
    ctx.drawImage(image,x,y,w,h,0,0,w,h);
    const data=ctx.getImageData(0,0,w,h);
    for(let py=0;py<h;py++) for(let px=0;px<w;px++) {
      const d=Math.hypot((px+0.5-w/2)/(w/2),(py+0.5-h/2)/(h/2));
      data.data[(py*w+px)*4+3]*=bounded((1-d)/0.19);
    }
    ctx.putImageData(data,0,0);
    return c;
  }
  const mouthPatch=patch(sourceByRegion.mouth,mouthROI);
  const morph = local.mouth_morph;
  let drawMorphedMouth = null;
  if (morph) {
    if (morph.method !== 'aligned-lip-grid') throw new Error('不支持的嘴部变形方法');
    const maxOpening=morph.max_opening ?? 0.72;
    if (!Number.isFinite(maxOpening) || maxOpening<=0 || maxOpening>1) throw new Error('嘴部最大开度须在 0 到 1 之间');
    // 两张纹理先变形到同一唇线，再在同一几何位置混合；不叠加两套唇线。
    const sourceCanvas=createCanvas(original.width,original.height),sc=sourceCanvas.getContext('2d');
    sc.drawImage(sourceByRegion.mouth,0,0);
    const openData=sc.getImageData(0,0,sourceCanvas.width,sourceCanvas.height).data;
    const [rx,ry,rw,rh]=mouthROI;
    const result=createCanvas(rw,rh),rc=result.getContext('2d');
    const states=[morph.closed,morph.open];
    for(const state of states) {
      if(!state || state.x.length!==7 || state.rows.length!==6 || state.rows.some(r=>r.length!==7)) throw new Error('唇线网格尺寸不合法');
      if(!state.x.every(Number.isFinite)||!state.rows.flat().every(Number.isFinite)) throw new Error('唇线网格包含非有限数值');
      for(let i=1;i<7;i++) if(state.x[i]<=state.x[i-1]) throw new Error('唇线网格横坐标必须递增');
      for(let c=0;c<7;c++) for(let r=1;r<6;r++) if(state.rows[r][c]<=state.rows[r-1][c]) throw new Error('唇线网格纵坐标必须递增');
      if(state.x[0]!==rx || state.x[6]!==rx+rw || state.rows[0].some(y=>y!==ry) || state.rows[5].some(y=>y!==ry+rh)) throw new Error('唇线网格外缘须固定在局部边界');
    }
    const mix=(a,b,t)=>a+(b-a)*t;
    const smooth=t=>t*t*(3-2*t);
    function sample(data,x,y,c) {
      x=Math.max(0,Math.min(original.width-1.001,x)); y=Math.max(0,Math.min(original.height-1.001,y));
      const ix=Math.floor(x),iy=Math.floor(y),fx=x-ix,fy=y-iy,k=(iy*original.width+ix)*4+c;
      return mix(mix(data[k],data[k+4],fx),mix(data[k+original.width*4],data[k+original.width*4+4],fx),fy);
    }
    drawMorphedMouth=(amount)=>{
      if(amount<=0.0001) return;
      const a=bounded(amount), targetX=states[0].x.map((x,i)=>mix(x,states[1].x[i],a));
      const data=rc.createImageData(rw,rh), textureBlend=smooth(bounded(a/0.24));
      for(let y=0;y<rh;y++) for(let x=0;x<rw;x++) {
        const px=rx+x,py=ry+y;
        let col=0; while(col<5 && px>targetX[col+1]) col++;
        const u=bounded((px-targetX[col])/(targetX[col+1]-targetX[col]));
        const lines=states.map(state=>state.rows.map(row=>mix(row[col],row[col+1],u)));
        const targetLines=lines[0].map((v,i)=>mix(v,lines[1][i],a));
        let row=0; while(row<4 && py>targetLines[row+1]) row++;
        const v=bounded((py-targetLines[row])/(targetLines[row+1]-targetLines[row]));
        const sx=states.map(state=>mix(state.x[col],state.x[col+1],u));
        const sy=lines.map(line=>mix(line[row],line[row+1],v));
        const edge=smooth(bounded(Math.min(x,y,rw-1-x,rh-1-y)/3));
        const dest=(y*rw+x)*4,baseIndex=(py*original.width+px)*4;
        for(let c=0;c<3;c++) {
          const color=mix(sample(baseData,sx[0],sy[0],c),sample(openData,sx[1],sy[1],c),textureBlend);
          data.data[dest+c]=Math.round(mix(baseData[baseIndex+c],color,edge));
        }
        data.data[dest+3]=255;
      }
      rc.putImageData(data,0,0);
      fctx.globalAlpha=1; fctx.drawImage(result,rx,ry);
    };
  }
  const eyePatches=eyeROIs.map(r=>patch(sourceByRegion.eyes,r));
  const face=createCanvas(original.width,original.height),fctx=face.getContext('2d');
  const width=Number(opt.width || 1080),height=Number(opt.height || 1440);
  if (![width,height].every(n=>Number.isInteger(n)&&n>0)) throw new Error('输出宽高须为正整数');
  if (width/height !== 3/4) throw new Error('试样须为 3:4');
  const crop=opt.crop?opt.crop.split(',').map(Number):(local.demo_crop || [280,40,480,640]);
  if (crop.length!==4 || !crop.every(Number.isFinite) || crop[0]<0 || crop[1]<0 || crop[2]<=0 || crop[3]<=0 || crop[0]+crop[2]>original.width || crop[1]+crop[3]>original.height || Math.abs(crop[2]/crop[3]-width/height)>0.0001) throw new Error('试样裁切不合法或比例不匹配');
  const canvas=createCanvas(width,height),ctx=canvas.getContext('2d');
  function draw(frame) {
    fctx.clearRect(0,0,face.width,face.height);
    fctx.globalAlpha=1;
    fctx.drawImage(base,0,0);
    const m=bounded(frame.mouth_openness)*(morph ? (morph.max_opening ?? 0.72) : 1);
    if(drawMorphedMouth) drawMorphedMouth(m);
    else if(m>0){ fctx.globalAlpha=m; fctx.drawImage(mouthPatch,mouthROI[0],mouthROI[1]); }
    const blink=bounded(frame.blink);
    if(blink>0) {
      fctx.globalAlpha=blink;
      eyePatches.forEach((p,i)=>fctx.drawImage(p,eyeROIs[i][0],eyeROIs[i][1]));
    }
    fctx.globalAlpha=1;
    ctx.clearRect(0,0,width,height);
    ctx.drawImage(face,...crop,0,0,width,height);
  }
  const outputPath=path.resolve(opt.output);
  fs.mkdirSync(path.dirname(outputPath),{recursive:true});
  const fps=motion.fps,duration=motion.duration_seconds;
  if (!Number.isFinite(fps)||fps<=0||!Number.isFinite(duration)||duration<=0) throw new Error('帧率与时长须为正数');
  if (motion.frame_count!==motion.frames.length || motion.frame_count!==Math.ceil(duration*fps)) throw new Error('运动帧数不匹配');
  for(let i=0;i<motion.frames.length;i++) {
    const f=motion.frames[i];
    if(![f.t,f.mouth_openness,f.blink].every(Number.isFinite)||Math.abs(f.t-i/fps)>1e-6||f.mouth_openness<0||f.mouth_openness>1||f.blink<0||f.blink>1) throw new Error('运动轨迹时间或数值不合法');
  }
  if(!Number.isFinite(motion.source_offset_seconds)||motion.source_offset_seconds<0||motion.source_offset_seconds+duration>motion.source_audio_duration_seconds+1e-6) throw new Error('声音窗口超出正式配音');
  const ffmpeg=opt.ffmpeg || 'ffmpeg';
  const ffprobe=opt.ffprobe || 'ffprobe';
  const encoder=spawn(ffmpeg,['-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgba','-s',`${width}x${height}`,'-r',String(fps),'-i','pipe:0','-ss',String(motion.source_offset_seconds),'-i',motion.source_audio_path,'-map','0:v:0','-map','1:a:0','-t',String(duration),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',outputPath],{stdio:['pipe','ignore','pipe']});
  let err=''; encoder.stderr.on('data',d=>err+=d);
  const done=new Promise((resolve,reject)=>{encoder.on('error',reject);encoder.on('close',code=>code===0?resolve():reject(new Error(`视频编码失败：${err}`)));});
  encoder.stdin.on('error',()=>{});
  const sampleFrames=new Set([0, motion.frames.reduce((b,f,i)=>f.mouth_openness>motion.frames[b].mouth_openness?i:b,0), motion.frames.reduce((b,f,i)=>f.blink>motion.frames[b].blink?i:b,0)]);
  const reviewed=[];
  let changesOutside=0, changedMouthFrames=0, changedEyeFrames=0;
  for (let i=0;i<motion.frames.length;i++) {
    draw(motion.frames[i]);
    if(motion.frames[i].mouth_openness>0) changedMouthFrames++;
    if(motion.frames[i].blink>0) changedEyeFrames++;
    if(sampleFrames.has(i)) {
      const current=fctx.getImageData(0,0,face.width,face.height).data;
      for(let py=0;py<face.height;py++) for(let px=0;px<face.width;px++) {
        if(rois.some(([x,y,w,h])=>px>=x&&px<x+w&&py>=y&&py<y+h)) continue;
        const k=(py*face.width+px)*4;
        if(current[k]!==baseData[k]||current[k+1]!==baseData[k+1]||current[k+2]!==baseData[k+2]||current[k+3]!==baseData[k+3]) changesOutside++;
      }
      const framePath=outputPath.replace(/\.mp4$/i,'')+`-frame-${String(i).padStart(3,'0')}.png`;
      fs.writeFileSync(framePath,canvas.toBuffer('image/png'));
      reviewed.push({frame:i,t:motion.frames[i].t,path:framePath,mouth_openness:motion.frames[i].mouth_openness,blink:motion.frames[i].blink});
    }
    if(!encoder.stdin.write(Buffer.from(ctx.getImageData(0,0,width,height).data))) await new Promise(resolve=>encoder.stdin.once('drain',resolve));
  }
  encoder.stdin.end(); await done;
  const probe=spawnSync(ffprobe,['-v','error','-show_entries','format=duration:stream=codec_type,width,height,r_frame_rate','-of','json',outputPath],{encoding:'utf8'});
  if(probe.status!==0) throw new Error(`媒体检查失败：${probe.stderr}`);
  const metadata=JSON.parse(probe.stdout);
  if(!metadata.streams.some(s=>s.codec_type==='audio')) throw new Error('试样缺声音');
  if(changesOutside!==0) throw new Error('嘴眼区域以外的原图被改变');
  const audit={schema_version:'1.0',status:'technical-pass-human-review-pending',sample_path:outputPath,sample_sha256:hash(outputPath),profile_path:profilePath,profile_sha256:hash(profilePath),motion_path:motionPath,motion_sha256:hash(motionPath),original_path:originalPath,original_sha256:hash(originalPath),source_audio_path:motion.source_audio_path,source_audio_sha256:motion.source_audio_sha256,source_offset_seconds:motion.source_offset_seconds,duration_seconds:duration,fps,width,height,crop,animated_regions:['mouth','eyes'],body_motion:'fixed',mouth_driver:'amplitude',phoneme_level_lip_sync:false,source_pixels_changed_outside_local_rois:changesOutside,pixel_check_scope:'闭嘴基线、最大嘴开合、最大眨眼三帧，编码前原分辨率像素对比；全部帧使用相同局部绘制流程',mouth_active_frame_count:changedMouthFrames,blink_active_frame_count:changedEyeFrames,review_frames:reviewed,media_probe:metadata,user_approved:false};
  audit.mouth_rendering=morph?'aligned-lip-morph':'legacy-opacity-overlay';
  fs.writeFileSync(outputPath.replace(/\.mp4$/i,'.audit.json'),JSON.stringify(audit,null,2)+'\n');
  console.log(JSON.stringify({sample_path:outputPath,duration_seconds:duration,frames:motion.frames.length,mouth_active_frames:changedMouthFrames,blink_active_frames:changedEyeFrames,changes_outside_rois:changesOutside,review_frames:reviewed},null,2));
}
main().catch(e=>{process.stderr.write(e.stack+'\n');process.exitCode=1;});
