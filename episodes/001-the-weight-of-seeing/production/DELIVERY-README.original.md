# 观看的重量 / The Weight of Seeing

A 3 minute 48 second, 1280 × 720, 24 fps bilingual visual essay.

## Watch

The higher-quality standalone master is delivered separately as `The-Weight-of-Seeing.mp4`. This source archive includes a compact offline copy at `site/dist/film.mp4`; open it in a standard video player, or open `site/dist/index.html` for the exhibition and transcript. The film contains burned-in Chinese/English subtitles and an original stereo electronic score. The companion SRT supplies the text separately. There is deliberately no narration.

Private presentation: https://weight-of-seeing.yydshly.chatgpt.site

## Artistic approach

Six movements: dwelling (Wang Meng, c. 1370); measure (Dürer, 1514); vulnerability (Hokusai, c. 1830–32); spectacle (Seurat, 1887–88); relations (an original response to 1920s Neo-Plasticism); and return (the present). This is a selective encounter across traditions, not a universal or comprehensive history, and not a claim of linear progress. The observations about inner life are the film's interpretation, not artists' quotations or diagnoses.

Full source images, close details, transitions and original moving reinterpretations are labeled in the frame. The geometric solid is an invented moving form, not an exact reconstruction of Dürer's polyhedron. The kinetic modernist composition is original, not an animated facsimile of a Mondrian painting. The final anonymous portrait is generated for the film; it is not a historical artwork or an identifiable real person.

## Source and rights

The four museum image files were supplied through The Metropolitan Museum of Art's Open Access API and each object returned `isPublicDomain: true`. `SOURCES.json` includes direct object links, image URLs, credit lines and SHA-256 hashes. The photographs are used under the museum's CC0/Open Access policy. The current Met image for Mondrian's Tableau is not open-access; it is not used.

All procedural motion, bilingual text and electronic music were produced for this film. The score uses mathematical synthesis, with no sampled commercial recording, stock song, purchased service or cloned voice. No claim of authorship by an unused model is made.

## Reproduce

Requirements: Python 3, NumPy, Pillow, FFmpeg with libx264/AAC. On the production machine, `/usr/bin/python3` supplies NumPy and Pillow. Noto CJK fonts provide both writing systems; update the font paths near the top of `render.py` if necessary.

1. `python3 score.py`
2. `python3 render.py --stills` (review keyframes)
3. `python3 render.py` (render silent master; 5,472 frames)
4. `ffmpeg -i output/film-silent.mp4 -i output/score.wav -map 0:v -map 1:a -c:v copy -af loudnorm=I=-19:TP=-2:LRA=9 -ar 48000 -c:a aac -b:a 128k -movflags +faststart The-Weight-of-Seeing.mp4`

`render.py --sample` creates the original 28-second motion test. The delivered full film supersedes it. The uncompressed temporary score and intermediate silent video are omitted from this archive; they can be reproduced from source.

## Accessibility

The page includes standard video controls, keyboard-accessible chapter seeking, a readable bilingual transcript and original-source links. No autoplay. No rapid flashing. Subtitles are always visible in the movie. Mobile viewers can use landscape/full-screen playback or read the transcript.
