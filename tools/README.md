# 可复现制作与观看审查

这组工具把艺术样段的素材证据、镜头时间、实际编码画面和听审入口放在一起。它不生成艺术判断，不把“能播放”写成用户认可，也不规定每部作品使用同一风格。

从仓库根目录运行：

```sh
python3 tools/review_study.py episodes/003-within-the-surface/study.json --validate-only
python3 tools/review_study.py episodes/003-within-the-surface/study.json --output product/review-003
python3 -m unittest discover -s tools -p 'test_*.py' -v
node tools/check_review_ui.cjs
python3 -m http.server 8000 --bind 127.0.0.1
```

打开 http://127.0.0.1:8000/product/review-003/。页面引用仓库中的原视频，不重复复制14MB文件。支持时间定位、源作品链接、浏览器本地笔记与当前笔记导出。完整目录移动后相对链接仍可工作；GitHub的源码页面不等于可运行网页。

运行条件：审查CLI使用Python 3.11+标准库与已安装的FFmpeg/ffprobe；页面事件测试需要Node。渲染器另需NumPy、Pillow、Noto CJK字体。没有网络请求、模型调用或新增费用；外部来源链接仅在观看者主动点击时打开。

## 单帧复现及新制作输出

```sh
python3 episodes/003-within-the-surface/production/render_study.py --frame 15.6 --output-dir /tmp/art-reproduction
python3 episodes/003-within-the-surface/production/render_study.py --stills --output-dir /tmp/art-preflight
# 明确需要重新生成完整研究样段时才执行：
python3 episodes/003-within-the-surface/production/render_study.py --output-dir /tmp/art-new-render
```

独立输出目录保护原交付文件。此阶段实际运行了两次单帧复现，未重渲染或延长36秒视频。环境与相同PNG哈希见product/review-003/environment.json。确定性针对当前环境与种子；不承诺不同编码器/字体/依赖版本的跨平台逐字节一致。

## 数据合同

每部作品用study.json显式记录艺术起始词、镜头区间、source/detail/interpretation/transition身份、双语标题、源素材、创作问题与认可状态。先从艺术材料建立镜头关系，再给出区间；此文件不应成为预设内容的固定模板。

校验拒绝：越界文件路径、素材字节或SHA256不符、缺来源字段、镜头空隙/重叠、非有限时间、漏连素材、缺双语标记和未说明认可状态。检查素材记录与本地文件一致，不等于重新法律审定每项授权；出处研究仍由创作者核查。

报告包含全段解码、时长/帧率、每段中点实际编码截图以及FFmpeg loudnorm输入测量。图片是时间锚点，不能证明整段无闪烁；响度不是音乐质量分数。人类听审、字幕逐段阅读和用户认可独立记录。

## 已知边界

当前云浏览器打开本地预览返回ERR_BLOCKED_BY_CLIENT，因此没有完成真实浏览器布局、播放或手机适配验证。Node只检查时间定位、保存、导出与存储失败事件。审查页可本地运行，此阶段未发布到原Site或公开作品展。
