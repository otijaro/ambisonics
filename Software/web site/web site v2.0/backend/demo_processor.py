# -*- coding: utf-8 -*-
import os,time,subprocess,logging
import numpy as np
import soundfile as sf
from backend.demo import (demo_normalize_audio,demo_stabilize_loudness,
 demo_stereo_to_foa,demo_foa_to_binaural,demo_foa_to_binaural_fallback,
 demo_foa_motion_original,demo_build_params,demo_apply_static_controls,demo_apply_motion)

logger=logging.getLogger("ambisonic-demo")
DEMO_MAX_SECONDS=15.0

def _restore_demo(result,reference_padding=512):
    if not isinstance(result,tuple): return result
    block,tl,tr=result; tail=np.stack([tl,tr],axis=1)
    missing=max(reference_padding-len(tail),0)
    if missing: tail=np.pad(tail,((0,missing),(0,0)))
    return np.concatenate([block,tail],axis=0)

def _mp3(wav,mp3):
    try:
        subprocess.Popen(["ffmpeg","-y","-loglevel","quiet","-i",wav,
                          "-codec:a","libmp3lame","-b:a","320k",mp3])
        return True
    except Exception as e:
        logger.error("MP3 DEMO: %s",e); return False

def process_demo(input_path,output_dir,direccion=0,altura=0,apertura=0,movimiento=0,
                 hrtf=None,pos=None,original_mode=True):
    t0=time.time(); os.makedirs(output_dir,exist_ok=True)

    # ÚNICA diferencia de carga: el DEMO solo lee los primeros 15 s.
    info=sf.info(input_path); sr=int(info.samplerate)
    frames=min(int(15.0*sr),int(info.frames))
    audio,sr=sf.read(input_path,frames=frames,dtype="float64",always_2d=True)

    # Desde aquí: misma ruta corta de processor.py.
    audio=audio.astype(np.float64)
    audio=audio-np.mean(audio,axis=0,keepdims=True)
    peak=np.max(np.abs(audio))+1e-9
    audio=0.95*audio/peak
    if audio.shape[1]<2: audio=np.repeat(audio,2,axis=1)

    r=demo_stereo_to_foa(audio,sr); W,X,Y,Z=r[0],r[1],r[2],r[3]
    p=demo_build_params(direccion,altura,apertura,movimiento)

    if original_mode: Ws,Xs,Ys,Zs=W,X,Y,Z
    else: Ws,Xs,Ys,Zs=demo_apply_static_controls(W,X,Y,Z,p["direccion_deg"],p["altura_pct"],p["apertura_pct"])

    if hrtf is not None and pos is not None:
        b=_restore_demo(demo_foa_to_binaural(Ws,Xs,Ys,Zs,sr,hrtf,pos,flip_az=False))
        b/=np.max(np.abs(b))+1e-9
    else: b=demo_foa_to_binaural_fallback(Ws,Xs,Ys,Zs)
    b=demo_normalize_audio(b,peak_target=0.95)

    if original_mode:
        W3,X3,Y3,Z3=demo_foa_motion_original(W,X,Y,Z,sr,0.12,0.10,60.0,3.5)
    elif p["movimiento_pct"]>0:
        W3,X3,Y3,Z3=demo_apply_motion(Ws,Xs,Ys,Zs,sr,p["movimiento_pct"])
    else: W3,X3,Y3,Z3=Ws,Xs,Ys,Zs

    if hrtf is not None and pos is not None:
        b3=_restore_demo(demo_foa_to_binaural(W3,X3,Y3,Z3,sr,hrtf,pos,flip_az=False))
        b3/=np.max(np.abs(b3))+1e-9
    else: b3=demo_foa_to_binaural_fallback(W3,X3,Y3,Z3)

    b3=0.90*b3+0.10*b
    b3=demo_stabilize_loudness(b3,sr,win_ms=450,strength=0.55,min_gain=0.88,max_gain=2)

    bw=os.path.join(output_dir,"preview_binaural.wav")
    dw=os.path.join(output_dir,"preview_3d_perceptual.wav")
    bm=os.path.join(output_dir,"preview_binaural.mp3")
    dm=os.path.join(output_dir,"preview_3d_perceptual.mp3")
    sf.write(bw,b,sr,subtype="PCM_16"); sf.write(dw,b3,sr,subtype="PCM_16")
    ok1=_mp3(bw,bm); ok2=_mp3(dw,dm)
    return {"sample_rate":sr,"duration_seconds":len(audio)/float(sr),
      "original_mode":bool(original_mode),"binaural_wav":bw,"binaural_mp3":bm if ok1 else None,
      "perceptual_wav":dw,"perceptual_mp3":dm if ok2 else None,
      "diagnostics_normal":{"direction_deg":0 if original_mode else p["direccion_deg"],
       "height_pct":0 if original_mode else p["altura_pct"],"width_pct":0 if original_mode else p["apertura_pct"]},
      "diagnostics_3d":{"movement_pct":"original" if original_mode else p["movimiento_pct"],
       "dynamic":True if original_mode else p["movimiento_pct"]>0}}

native_process_demo=process_demo
