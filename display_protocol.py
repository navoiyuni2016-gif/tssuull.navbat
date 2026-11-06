"""User-defined LED frames. No vendor protocol or default wire frame is guessed."""
import ipaddress
import re
import socket
import time

TOKENS={'address8','address_ascii','label_ascii','number_ascii','number_le16','number_be16','window8','xor8','sum8','modbus16'}
class SendError(Exception):
    def __init__(self,message,uncertain=False):super().__init__(message);self.uncertain=uncertain

def frame(template,device,label,window):
    if not isinstance(template,str) or not template.strip() or len(template)>2000:raise ValueError('HEX buyruq shabloni kerak (2000 belgigacha)')
    if not isinstance(label,str) or not re.fullmatch('[A-Z0-9]{1,12}',label):raise ValueError('Tablo qiymati 1–12 katta lotin harfi/raqam bo‘lsin')
    result=bytearray();checksums=0
    parts=re.split(r'(\{[^{}]*\})',template)
    for part in parts:
        if not part:continue
        if part.startswith('{'):
            token=part[1:-1]
            if token not in TOKENS:raise ValueError('Nomaʼlum shablon belgisi: '+token)
            if token=='address8':value=int(device['device_address']);chunk=bytes([value])
            elif token=='address_ascii':chunk=device['device_address'].encode('ascii')
            elif token=='label_ascii':chunk=label.encode('ascii')
            elif token=='window8':chunk=bytes([window])
            elif token.startswith('number_'):
                match=re.search(r'\d+$',label)
                if not match:raise ValueError('Chiptada raqam yo‘q')
                chunk=match[0].encode('ascii') if token=='number_ascii' else int(match[0]).to_bytes(2,'little' if token=='number_le16' else 'big')
            else:
                checksums+=1
                if checksums>1:raise ValueError('Bir shablonda bitta checksum bo‘lsin')
                start=device.get('profile',{}).get('checksum_start') or 0
                if start>len(result):raise ValueError('Checksum boshlanishi paketdan tashqarida')
                data=result[start:]
                if token=='sum8':chunk=bytes([sum(data)&255])
                elif token=='xor8':
                    value=0
                    for byte in data:value^=byte
                    chunk=bytes([value])
                else:
                    value=0xffff
                    for byte in data:
                        value^=byte
                        for _ in range(8):value=(value>>1)^0xa001 if value&1 else value>>1
                    chunk=value.to_bytes(2,'little')
        else:
            if not re.fullmatch(r'[0-9A-Fa-f\s]*',part):raise ValueError('Shablonda faqat HEX baytlar va {belgi} ishlatiladi')
            chunk=bytes.fromhex(part)
        result.extend(chunk)
        if len(result)>512:raise ValueError('Tablo paketi 512 baytdan oshmasin')
    if not result:raise ValueError('Bo‘sh buyruq yuborilmaydi')
    return bytes(result)

def prepare(device,value,operation):
    p=device.get('profile',{})
    if p.get('protocol')!='manual_hex':raise ValueError('Qurilma protokolini qo‘lda HEX shablon sifatida kiriting')
    required=['timeout_ms','show_template','clear_template']
    if device['transport']=='serial':required+=['baud_rate','data_bits','parity','stop_bits']
    elif device['transport']=='tcp':
        required+=['tcp_port']
        try:ipaddress.ip_address(device['endpoint'])
        except ValueError:raise ValueError('IP manzilni portdan alohida kiriting')
    else:raise ValueError('Qo‘lda profil COM yoki IP ulanishida ishlaydi; agent hali qo‘llanmaydi')
    if any(p.get(k) in (None,'') for k in required):raise ValueError('Port parametrlari, timeout va ikkala HEX shablonni to‘ldiring')
    # Validate both commands, including clear; never supply a default blanking frame.
    if any(token in p['clear_template'] for token in ('{label_ascii}','{number_ascii}','{number_le16}','{number_be16}')):raise ValueError('Tozalash shabloni chiptaga bog‘liq bo‘lmasin; kerakli bo‘sh belgilarni HEXda yozing')
    show=frame(p['show_template'],device,value,device['window'])
    clear=frame(p['clear_template'],device,value,device['window'])
    return clear if operation=='clear' else show

def send(device,payload):
    p=device['profile'];timeout=p['timeout_ms']/1000
    if device['transport']=='tcp':
        try:connection=socket.create_connection((device['endpoint'],p['tcp_port']),timeout)
        except OSError as exc:raise SendError('LED IP ulanilmadi: '+str(exc)) from exc
        try:
            connection.settimeout(timeout);connection.sendall(payload)
        except OSError as exc:raise SendError('LED IP yuborish natijasi nomaʼlum: '+str(exc),True) from exc
        finally:connection.close()
        return
    if device['transport']!='serial':raise SendError('Ulanish turi qo‘llanmaydi')
    try:import serial
    except ImportError as exc:raise SendError('COM moduli mavjud emas. EXE paketini yangilang yoki pyserial o‘rnating.') from exc
    try:port=serial.Serial(device['endpoint'],baudrate=p['baud_rate'],bytesize=p['data_bits'],parity=p['parity'],stopbits=float(p['stop_bits']),timeout=timeout,write_timeout=timeout)
    except (OSError,ValueError,serial.SerialException) as exc:raise SendError('LED COM ochilmadi: '+str(exc)) from exc
    try:
        if port.write(payload)!=len(payload):raise SendError('LED baytlari qisman yuborildi',True)
        deadline=time.monotonic()+timeout
        while port.out_waiting:
            if time.monotonic()>=deadline:raise SendError('LED COM navbati vaqtida bo‘shamadi',True)
            time.sleep(.01)
    except SendError:raise
    except (OSError,serial.SerialException) as exc:raise SendError('LED COM yuborish natijasi nomaʼlum: '+str(exc),True) from exc
    finally:port.close()
