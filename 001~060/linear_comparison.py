import vapoursynth as vs
import rksfunc as rks
import os
import random
from awsmfunc import FrameInfo
from math import ceil
from mvsfunc import ToRGB

core = vs.core
core.max_cache_size = 25600

random.seed(19260817)  # 随机种子不变抽出来的图不变
sample_itv = 5000  # 平均每多少帧抽检一次
start_num = 1
num_len = 4
crop_param = 240, 240
style = ("Consolas,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,7,10,10,10,1")

filelist = os.listdir()
srclist = [fn for fn in filelist if fn.endswith('.m2ts')]
dstlist = [fn for fn in filelist if fn.endswith('.mkv')]  # 也可以把 .mkv 改成 .hevc
os.makedirs('src', exist_ok=True)
os.makedirs('rip', exist_ok=True)

def torgb(clip: vs.VideoNode) -> vs.VideoNode:
    return ToRGB(rks.uvsr(clip), depth=8)
    
for srcfn, dstfn in zip(srclist, dstlist):
    src = rks.sourcer(srcfn).std.Crop(*crop_param)
    dst = rks.sourcer(dstfn)
    src = FrameInfo(torgb(src), 'Source', style)
    dst = FrameInfo(torgb(dst), 'Rip', style)
    num_frames = src.num_frames if src.num_frames == dst.num_frames else 0
    if num_frames == 0:
        continue
    sample_num = ceil(num_frames / sample_itv)
    sample_idx = random.sample(list(range(num_frames)), min(sample_num, num_frames))
    srcset, dstset = None, None
    for idx in sample_idx:
        src.get_frame(idx)
        if srcset is None:
            srcset = src[idx]
        else:
            srcset = srcset + src[idx]
        if dstset is None:
            dstset = dst[idx]
        else:
            dstset = dstset + dst[idx]
    out = srcset.imwri.Write('PNG', f'./src/%0{num_len}dsrc.png', start_num, overwrite=True) + \
        dstset.imwri.Write('PNG', f'./rip/%0{num_len}drip.png', start_num, overwrite=True)
    for frame in out.frames(close=True):
        pass
    start_num += srcset.num_frames
