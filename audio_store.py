"""Local recordings. No archives, executable content or user-supplied paths."""
import base64
import hashlib
import io
import re
import wave
import tempfile

MAX_AUDIO = 8 * 1024 * 1024
SLOT = re.compile(r'^(attention|ticket|window|prefix_[A-Z]{1,3}|digit_[0-9]|window_[1-9][0-9]?|window_100|number_[1-9][0-9]{0,3})$')


def save(connection, directory, body):
    slot = body.get('slot', '')
    if not isinstance(slot, str) or not SLOT.fullmatch(slot):
        raise ValueError('Noto‘g‘ri ovoz belgisi')
    if body.get('rights_confirmed') is not True:
        raise ValueError('Ovozdan foydalanish huquqini tasdiqlang')
    encoded = body.get('content', '')
    if not isinstance(encoded, str) or len(encoded) > (MAX_AUDIO * 4 // 3 + 8):
        raise ValueError('Ovoz fayli 8 MB dan oshmasin')
    try:
        content = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as error:
        raise ValueError('Ovoz fayli buzilgan') from error
    if not content or len(content) > MAX_AUDIO:
        raise ValueError('Bo‘sh yoki juda katta ovoz fayli')
    name = body.get('name', '')
    if not isinstance(name, str) or not 1 <= len(name) <= 200:
        raise ValueError('Fayl nomi noto‘g‘ri')
    if name.lower().endswith('.wav'):
        try:
            with wave.open(io.BytesIO(content), 'rb') as audio:
                if audio.getnchannels() not in (1, 2) or not 8000 <= audio.getframerate() <= 96000 or audio.getnframes() / audio.getframerate() > 120:
                    raise ValueError('WAV: mono/stereo PCM, 8–96 kHz, 120 soniyagacha')
                if len(audio.readframes(audio.getnframes())) != audio.getnframes() * audio.getnchannels() * audio.getsampwidth():
                    raise ValueError('WAV fayli to‘liq emas')
        except (wave.Error, EOFError) as error:
            raise ValueError('Haqiqiy PCM WAV faylini tanlang') from error
        mime = 'audio/wav'
    elif name.lower().endswith('.mp3') and (content[:3] == b'ID3' or (len(content) > 1 and content[0] == 255 and content[1] & 224 == 224)):
        mime = 'audio/mpeg'
    else:
        raise ValueError('Faqat PCM WAV yoki MP3 fayllari qabul qilinadi')
    digest = hashlib.sha256(content).hexdigest()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / digest
    # Content-addressed blobs: an update cannot partially overwrite an active file.
    if not path.exists():
        with tempfile.NamedTemporaryFile(dir=directory, delete=False) as output:
            temporary = directory / output.name
            output.write(content)
        temporary.replace(path)
    connection.execute('INSERT INTO audio(slot,name,mime,digest) VALUES (?,?,?,?) ON CONFLICT(slot) DO UPDATE SET name=excluded.name,mime=excluded.mime,digest=excluded.digest', (slot, name, mime, digest))
    return {'slot': slot, 'name': name, 'url': '/audio/' + digest, 'mime': mime}


def manifest(connection):
    return {row['slot']: {'name': row['name'], 'url': '/audio/' + row['digest'], 'mime': row['mime']} for row in connection.execute('SELECT * FROM audio ORDER BY slot')}
