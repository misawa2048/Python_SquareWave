#import librosa
#import librosa.display
#!/usr/bin/python 
# based on : www.daniweb.com/code/snippet263775.html
import math
import wave
import struct

class TextToWav():
    sample_rate = 16000
    pulse_hz = 1200
    volume = 0.5

    def __init__(self,samplerate,volume):
        self.sample_rate = 16000
        self.volume = 0.5
        self.pulse_hz = 1200
        self.audio=[]

    def clear(self):
        self.audio=[]

    def append_silence(self, _audio, duration_milliseconds=1000):
        num_samples = duration_milliseconds * (self.sample_rate / 1000.0)
        for x in range(int(num_samples)): 
            _audio.append(0.0)

        return _audio

    def append_sinPulse(self, _audio, _pulse_bit=0, _pulseNum=1):
        per_samples = self.sample_rate / (self.pulse_hz*(_pulse_bit+1))
        for x in range(int(_pulseNum * per_samples)):
            val =  self.volume * math.sin(2 * math.pi * ( x / per_samples ));
            _audio.append(val)
        return _audio

    def append_bytes_to_tone(self, _audio, _data:bytes, _max_bytes=100000):
        if(_max_bytes<=0):
            _max_bytes = len(_data)
        else:
            _max_bytes = min(_max_bytes,len(_data))
            
        for idx in range(_max_bytes):
            _audio = self.append_sinPulse(_audio, 0, 1) # start bit 
            for b in range(8):
                onbit = ((_data[idx]>>b)&1) # off=0,on=1
                _audio = self.append_sinPulse(_audio, onbit, 1) # data bit 

            _audio = self.append_sinPulse(_audio, 1, 2) # stop bit 

        return _audio

    def save_wav(self, _audio, _filename, _callback=None):
        # Open up a wav file
        wav_file=wave.open(_filename,"w")

        # wav params
        nchannels = 1
        sampwidth = 2

        # 44100 is the industry standard sample rate - CD quality.  If you need to
        # save on file size you can adjust it downwards. The stanard for low quality
        # is 8000 or 8kHz.
        nframes = len(_audio)
        comptype = "NONE"
        compname = "not compressed"
        wav_file.setparams((nchannels, sampwidth, self.sample_rate, nframes, comptype, compname))

        # WAV files here are using short, 16 bit, signed integers for the 
        # sample size.  So we multiply the floating point data we have by 32767, the
        # maximum value for a short integer.  NOTE: It is theortically possible to
        # use the floating point -1.0 to 1.0 data directly in a WAV file but not
        # obvious how to do that using the wave module in python.
        for sample in _audio:
            wav_file.writeframesraw(struct.pack('h', int( sample * 32767.0 )))

        wav_file.close()

        return None if _callback==None else _callback()

    def bin_to_wav(self, _bindata:bytes,_filename,_callback=None):
        self.audio = []
        #http://ngs.no.coocan.jp/doc/wiki.cgi/TechHan?page=2%BE%CF+%A5%AB%A5%BB%A5%C3%A5%C8%8E%A5%A5%A4%A5%F3%A5%BF%A1%BC%A5%D5%A5%A7%A5%A4%A5%B9

        self.audio = self.append_sinPulse(self.audio,1,16000)
        self.audio = self.append_bytes_to_tone(self.audio,b'\xd3\xd3\xd3\xd3\xd3\xd3\xd3\xd3\xd3\xd3') #0xD3 x 10
        self.audio = self.append_bytes_to_tone(self.audio, (filename+".cas").encode('utf-8')) # filename
        self.audio = self.append_silence(self.audio,1700) # space
        self.audio = self.append_sinPulse(self.audio,1,4000) # short header
        self.audio = self.append_bytes_to_tone(self.audio, _bindata,10000) # data body
        self.audio = self.append_sinPulse(self.audio, 0, 7) # end of data

        return self.save_wav(self.audio,_filename+".wav",_callback)

    def text_to_wav(self, _text:str, _filename,_callback=None):
        bindata = _text.encode()
        return self.bin_to_wav(bindata, _filename,_callback)

    def debug_disp_bindata(self,_bindata):
        print("--------------------------------------------------------------------")
        print (_bindata)
        print("--------------------------------------------------------------------")

        datCnt=0
        for data in _bindata:
            print(data,)
            datCnt+=1
            if(datCnt>20):
                break

    def debug_disp_bytes(self,_data:bytes, _max_bytes=100000):
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


import urllib.request
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.planeText = ""

    def handle_data(self, data):
        self.planeText += data
        #print("Encountered some data  :", data)


def get_htmlstr_from_url(_url):
    req = urllib.request.Request(_url)
    with urllib.request.urlopen(req) as res:
        body = res.read()
    #print(res.status)

    _htmlstr="?"
    try:
        _htmlstr=body.decode('utf-8')
    except UnicodeDecodeError:
        pass
    return _htmlstr

def htmlstr_to_planestr(_htmlstr):
    parser = MyHTMLParser()
    parser.feed(_htmlstr)
    return parser.planeText

def finished():
    print("FINISHED!")
    
# Audio will contain a long list of samples (i.e. floating point numbers describing the
# waveform).  If you were working with a very long sound you'd want to stream this to
# disk instead of buffering it all in memory list this.  But most sounds will fit in 
# memory.

#坊ちゃん
#def_url = "https://www.aozora.gr.jp/cards/000148/files/752_14964.html"
#Qiita記事
#def_url = "https://qiita.com/hoto17296/items/8fcf55cc6cd823a18217"
#The Wonderful Wizard of Oz
def_url = "http://www.gutenberg.org/files/55/55.txt"


filename = "testprog" # filename.cas -> filename.wav

htmlstr = get_htmlstr_from_url(def_url)
planestr = htmlstr_to_planestr(htmlstr)

t2w = TextToWav(samplerate=16000, volume=0.5)

print("saving ",filename+".wav")

#t2w.text_to_wav(planestr, filename, finished)

bindata = planestr.encode()

#t2w.debug_disp_bindata(bindata)
#t2w.debug_disp_bytes(bindata)

t2w.bin_to_wav(bindata,filename,finished)


print("save complete.")
