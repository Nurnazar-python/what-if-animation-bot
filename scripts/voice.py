"""Step 2: the voice. Edge-TTS (Microsoft Edge neural voices) with stable-whisper alignment, then pauses tightened to the genre's pace.

python <skill>/scripts/voice.py <slug> [--force]
Reads  src/episodes/<slug>/episode.json  (script, voice, gaps)
Writes public/<slug>/voice_raw.wav, public/<slug>/voice.wav (tightened), src/episodes/<slug>/words.json (word timings
       after tightening, used by plan.py) and out/<slug>/words_raw.json.
The API is only called when the text or the voice settings change (cached by a hash), so re-running to retune the
gaps is free.

episode.json "voice" (all optional):
  {"voice": "en-US-GuyNeural", "rate": "+0%", "pitch": "+0Hz"}
episode.json "gaps" (seconds, all optional):
  {"word": 0.12, "comma": 0.2, "sentence": 0.3, "question": 0.45,
   "pairs": {"anything|One": 0.6}}  -> every pause longer than its limit is cut to the limit, from its middle.
"""
import asyncio, hashlib, json, re, sys, time, os, subprocess, tempfile
from pathlib import Path

import numpy as np

from wi import SR, decode, ep_dir, load_episode, load_json, log_cost, out_dir, pub_dir, save_json, write_wav

slug = sys.argv[1]
force = '--force' in sys.argv
ep = load_episode(slug)

# Default Edge-TTS voice (male, natural, good for narration)
V = {'voice': 'en-US-GuyNeural', 'rate': '+0%', 'pitch': '+0Hz'}
V.update(ep.get('voice', {}))

text = ' '.join(b['text'].strip() for b in ep['script'])
sig = hashlib.sha1(json.dumps([text, V], sort_keys=True).encode()).hexdigest()[:12]
raw_wav = pub_dir(slug) / 'voice_raw.wav'
raw_words = out_dir(slug) / 'words_raw.json'
meta = load_json(out_dir(slug) / 'voice_meta.json', {})

if force or meta.get('sig') != sig or not raw_wav.exists() or not raw_words.exists():
    print(f'{len(text)} characters to Edge-TTS (voice {V["voice"]})')
    t0 = time.time()

    # ---- Edge-TTS ----
    import edge_tts

    async def synthesize():
        communicate = edge_tts.Communicate(text, V['voice'], rate=V.get('rate', '+0%'), pitch=V.get('pitch', '+0Hz'))
        await communicate.save(str(raw_wav))

    asyncio.run(synthesize())

    # ---- stable-whisper alignment (Whisper-based) ----
    import stable_whisper
    import stable_whisper.alignment

    # Load a small Whisper model for alignment (fast, accurate enough)
    model = stable_whisper.load_model('tiny', device='cpu')
    # Force alignment with known text
    result = stable_whisper.alignment.align(model, str(raw_wav), text, 'en', verbose=False)
    words = []
    for segment in result.segments:
        for w in segment.words:
            words.append({
                'w': w.word.strip(),
                's': round(w.start, 3),
                'e': round(w.end, 3),
                'p': ''
            })

    # Punctuation: restore from original text
    original_words = re.findall(r"[\w']+|[.,!?;:…—\-]", text)
    idx = 0
    for w in words:
        punct = ''
        while idx < len(original_words) and not re.match(r"[\w']", original_words[idx]):
            idx += 1
        if idx < len(original_words):
            if w['w'].lower() == original_words[idx].lower().rstrip(".,!?;:…—\\-"):
                if idx + 1 < len(original_words) and re.match(r"[.,!?;:…—\-]", original_words[idx + 1]):
                    punct = original_words[idx + 1]
                    idx += 1
            idx += 1
        w['p'] = punct

    save_json(raw_words, words)
    save_json(out_dir(slug) / 'voice_meta.json', {'sig': sig, 'chars': len(text)})

    # Edge-TTS is free, no credits
    log_cost(slug, 'voice', 0, f'{len(text)} characters (Edge-TTS, free)')
else:
    print('Voice unchanged since the last call: reusing it (no credits).')

# ---------------------------------------------------------------- tighten the pauses
words = load_json(raw_words)
G = {'word': 0.12, 'comma': 0.2, 'sentence': 0.3, 'question': 0.45, 'pairs': {}}
G.update(ep.get('gaps', {}))
x = decode(raw_wav)
cuts = []


def bare(w):
    return re.sub(r'[^\w]', '', w)


for a, b in zip(words, words[1:]):
    gap = b['s'] - a['e']
    key = bare(a['w']) + '|' + bare(b['w'])
    if key in G['pairs']:
        keep = G['pairs'][key]
    elif '?' in a['p'] or '!' in a['p']:
        keep = G['question']
    elif '.' in a['p'] or ':' in a['p'] or ';' in a['p'] or '…' in a['p']:
        keep = G['sentence']
    elif ',' in a['p'] or '—' in a['p'] or '-' in a['p']:
        keep = G['comma']
    else:
        keep = G['word']
    if gap > keep:
        mid = (a['e'] + b['s']) / 2
        rm = gap - keep
        cuts.append((mid - rm / 2, mid + rm / 2))
parts, last = [], 0.0
for s, e in cuts:
    parts.append(x[int(last * SR):int(s * SR)])
    last = e
parts.append(x[int(last * SR):])
fade = int(0.004 * SR)  # a 4 ms fade either side of each join, so no click
for i, part in enumerate(parts):
    part = part.copy()
    if i > 0 and len(part) > fade:
        part[:fade] *= np.linspace(0, 1, fade)
    if i < len(parts) - 1 and len(part) > fade:
        part[-fade:] *= np.linspace(1, 0, fade)
    parts[i] = part
y = np.concatenate(parts)
write_wav(pub_dir(slug) / 'voice.wav', y)


def shift(t):
    return t - sum(min(e, t) - s for s, e in cuts if t > s)


out = [{'w': w['w'], 's': round(shift(w['s']), 3), 'e': round(shift(w['e']), 3), 'p': w.get('p', '')} for w in words]
save_json(ep_dir(slug) / 'words.json', out)
print(f'Tightened {len(cuts)} pauses, removed {sum(e - s for s, e in cuts):.2f} s: {len(x) / SR:.2f} s -> {len(y) / SR:.2f} s')
print(' '.join(f"{w['w']}@{w['s']}" for w in out))