#import librosa
#import librosa.display
#!/usr/bin/python 
# based on : www.daniweb.com/code/snippet263775.html
import math
import wave
import struct
import urllib.request
from html.parser import HTMLParser

#坊ちゃん
#def_url = "https://www.aozora.gr.jp/cards/000148/files/752_14964.html"
#Qiita記事
#def_url = "https://qiita.com/hoto17296/items/8fcf55cc6cd823a18217"
#The Wonderful Wizard of Oz
#def_url = "http://www.gutenberg.org/files/55/55.txt"

#simple html
def_url = "https://elix-jp.sakura.ne.jp/api/usage.php"

def append_sinPulse(_audio, _sample_rate=16000, _pulse_hz=1200, _pulseNum=1, _volume=0.5):
    per_samples = _sample_rate / _pulse_hz
    for x in range(int(_pulseNum * per_samples)):
        val =  _volume * math.sin(2 * math.pi * ( x / per_samples ));
        _audio.append(val)
    return _audio

def append_bytes_to_tone(_data:bytes, _audio, _sample_rate=16000, _pulse_hz=1200, _volume=0.5, _max_bytes=100000):
    if(_max_bytes<=0):
        _max_bytes = len(_data)
    else:
        _max_bytes = min(_max_bytes,len(_data))
        
    for idx in range(_max_bytes):
        append_sinPulse(_audio, _sample_rate, _pulse_hz, 1, _volume) # start bit 
        for b in range(8):
            onbit = ((_data[idx]>>b)&1)+1 # off=1,on=2
            append_sinPulse(_audio, _sample_rate, _pulse_hz*onbit, 1, _volume) # data bit 

        append_sinPulse(_audio, _sample_rate, _pulse_hz*2, 2, _volume) # stop bit 

    return _audio

def debug_disp_bytes(_data:bytes, _audio, _sample_rate=16000, _pulse_hz=1200, _volume=0.5, _max_bytes=100000):
    if(_max_bytes<=0):
        _max_bytes = len(_data)
    else:
        _max_bytes = min(_max_bytes,len(_data))
        
    for idx in range(_max_bytes):
        bstr="0"
        for b in range(8):
            onbit = ((_data[idx]>>b)&1)+1 # off=1,on=2
            bstr += str(onbit-1)

        bstr += "11"
        print(bstr)

def append_silence(_audio, _sample_rate=16000, duration_milliseconds=1000):
    """
    Adding silence is easy - we add zeros to the end of our array
    """
    num_samples = duration_milliseconds * (_sample_rate / 1000.0)

    for x in range(int(num_samples)): 
        _audio.append(0.0)

    return _audio

def save_wav(_audio, file_name):
    # Open up a wav file
    wav_file=wave.open(file_name,"w")

    # wav params
    nchannels = 1
    sampwidth = 2

    # 44100 is the industry standard sample rate - CD quality.  If you need to
    # save on file size you can adjust it downwards. The stanard for low quality
    # is 8000 or 8kHz.
    nframes = len(_audio)
    comptype = "NONE"
    compname = "not compressed"
    wav_file.setparams((nchannels, sampwidth, sample_rate, nframes, comptype, compname))

    # WAV files here are using short, 16 bit, signed integers for the 
    # sample size.  So we multiply the floating point data we have by 32767, the
    # maximum value for a short integer.  NOTE: It is theortically possible to
    # use the floating point -1.0 to 1.0 data directly in a WAV file but not
    # obvious how to do that using the wave module in python.
    for sample in _audio:
        wav_file.writeframesraw(struct.pack('h', int( sample * 32767.0 )))

    wav_file.close()
    return wav_file

def get_utf8str_from_url(_url):
    req = urllib.request.Request(_url)
    with urllib.request.urlopen(req) as res:
        body = res.read()
    #print(res.status)

    _utf8str="?"
    try:
        _utf8str=body.decode('utf-8')
    except UnicodeDecodeError:
        pass
    return _utf8str

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.planeText = ""

    def handle_data(self, data):
        self.planeText += data
        #print("Encountered some data  :", data)

def utf8str_to_bindata(_utf8str):
    parser = MyHTMLParser()
    parser.feed(_utf8str)

    _bindata = parser.planeText.encode()

    return _bindata

def debug_disp_bindata(_bindata):
    print("--------------------------------------------------------------------")
    print (_bindata)
    print("--------------------------------------------------------------------")

    datCnt=0
    for data in _bindata:
        print(data,)
        datCnt+=1
        if(datCnt>20):
            break

def bin_to_wav(_bindata:bytes, _filename, _sample_rate, _volume):
    _audio = []
    #http://ngs.no.coocan.jp/doc/wiki.cgi/TechHan?page=2%BE%CF+%A5%AB%A5%BB%A5%C3%A5%C8%8E%A5%A5%A4%A5%F3%A5%BF%A1%BC%A5%D5%A5%A7%A5%A4%A5%B9
    _audio = append_sinPulse(_audio, _sample_rate,2400,16000,_volume) # long header 16000 -> 8000
    _audio = append_bytes_to_tone(b'\xd3\xd3\xd3\xd3\xd3\xd3\xd3\xd3\xd3\xd3', _audio, _sample_rate, 1200,_volume,1000) #0xD3 x 10
    _audio = append_bytes_to_tone( (filename+".cas").encode('utf-8'), _audio, _sample_rate, 1200,_volume,1000) # filename
    _audio = append_silence(_audio,_sample_rate,1700) # space
    _audio = append_sinPulse(_audio, _sample_rate,2400,4000,_volume) # short header
    _audio = append_bytes_to_tone(_bindata, _audio, _sample_rate, 1200,_volume,10000) # data body
    _audio = append_sinPulse(_audio, _sample_rate,1200,7,_volume) # end of data
    save_wav(_audio,_filename+".wav")


# Audio will contain a long list of samples (i.e. floating point numbers describing the
# waveform).  If you were working with a very long sound you'd want to stream this to
# disk instead of buffering it all in memory list this.  But most sounds will fit in 
# memory.
sample_rate = 16000.0
filename = "testprog" # filename.cas -> filename.wav
volume = 0.5

utf8str = get_utf8str_from_url(def_url)
bindata = utf8str_to_bindata(utf8str)

print("saving ",filename+".wav")
bin_to_wav(bindata,filename,sample_rate,volume)
print("save complete.")
