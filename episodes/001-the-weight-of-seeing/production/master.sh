#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
ffprobe -v error -show_entries stream=nb_frames -of csv=p=0 output/film-silent.mp4 | grep -qx 5472
ffmpeg -y -i output/film-silent.mp4 -i output/score.wav -map 0:v -map 1:a -c:v copy -af 'loudnorm=I=-19:TP=-2:LRA=9:measured_I=-14.89:measured_TP=-2.85:measured_LRA=4.30:measured_thresh=-25.00:offset=0.34:linear=true' -ar 48000 -c:a aac -b:a 160k -metadata title='观看的重量 / The Weight of Seeing' -metadata comment='Bilingual visual essay. Original motion and score. Museum images: The Met Open Access / CC0.' -movflags +faststart output/The-Weight-of-Seeing.mp4 > output/master-mux.log 2>&1
# Browser edition stays below the hosting per-asset limit. The Library master remains higher quality.
ffmpeg -y -i output/The-Weight-of-Seeing.mp4 -an -c:v libx264 -threads 2 -preset slow -b:v 740k -pass 1 -passlogfile output/web-pass -f mp4 /dev/null > output/web-pass1.log 2>&1
ffmpeg -y -i output/The-Weight-of-Seeing.mp4 -c:v libx264 -threads 2 -preset slow -b:v 740k -pass 2 -passlogfile output/web-pass -c:a aac -b:a 112k -ar 48000 -movflags +faststart site/dist/film.mp4 > output/web-pass2.log 2>&1
ffprobe -v error -show_format -show_streams -of json output/The-Weight-of-Seeing.mp4 > qa/master-probe.json
ffprobe -v error -show_format -show_streams -of json site/dist/film.mp4 > qa/web-probe.json
ffmpeg -v error -i output/The-Weight-of-Seeing.mp4 -f null - 2> qa/master-decode-errors.txt
ffmpeg -v error -i site/dist/film.mp4 -f null - 2> qa/web-decode-errors.txt
printf 'Master and web edition encoded and fully decoded.\n'
