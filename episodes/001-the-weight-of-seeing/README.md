# 001 · 观看的重量 / The Weight of Seeing

状态：成片已完成，用户已观看并给予正面反馈。这里不据此声称作品达到任何客观的“大师级”评级。

## 观看与源文件

- [作品网页](https://weight-of-seeing.yydshly.chatgpt.site)，私密
- [完整聊天发送版 MP4](media/The-Weight-of-Seeing-Mobile.mp4)，16,928,325 bytes
- [较高码率母版 MP4](media/The-Weight-of-Seeing.mp4)，52,924,421 bytes
- [双语字幕](media/The-Weight-of-Seeing.zh-en.srt)
- [分镜](STORYBOARD.md)
- [原始请求与后续修订](prompts/01-user-request-verbatim.md)
- [制作说明：复盘整理](prompts/02-production-brief.md)
- [实际图像生成提示词](prompts/03-image-generation-verbatim.txt)
- [馆藏来源、许可与哈希](production/SOURCES.json)
- [技术检查](qa/technical-qa.json)

完整时长约 228 秒，24 fps，1280×720；不同封装的时长可能因 AAC 尾部样本相差约 0.01 秒。16.93 MB 版本是完整成片，不是节选。网页保留 24.49 MB 播放版；仓库母版保留较高码率图像。

## 复现

源代码位于 `production/`。需要 Python 3、NumPy、Pillow、FFmpeg 与 Noto CJK 字体。

```sh
cd production
mkdir -p output qa site/dist
python3 score.py
python3 render.py --stills
python3 render.py
bash master.sh
```

`master.sh` 还输出网页播放版到 `site/dist`；上面的命令已创建需要的目录。字体路径写在 `render.py` 开头，需要与本机安装位置一致。`fetch_assets.py` 是可选的原图重新获取工具，需要 requests；归档已包含已核验原图，正常复现不需要再次联网下载。

## 已核验和限制

已检查：全部 5,472 帧渲染；主片、网页版与聊天版完整解码无错误；两种语言字幕安全区；实际编码后关键画面；原作权利标记；最终片尾；音频综合响度约 -19.0 LUFS、真峰值约 -7.0 dBFS。

限制：浏览器实际播放、移动端布局和交互检查因本地预览访问限制未完成；六章跳转逻辑与文件引用做了独立检查。技术声学分析已完成，但不把它称作人工听审。全片为 720p，不能称作原生 4K。历史路径有选择性，不代表对全部文化、时期与美学理论的概括。

## 本片留下的可复用经验

字幕保持简洁，运动规则随命题改变；公开可看的图片仍要逐件核验使用条件；成片交付必须考虑聊天文件大小。下一期应更聚焦一个具体观点，避免把系列锁定为“多时代名画加总结”的固定结构。
