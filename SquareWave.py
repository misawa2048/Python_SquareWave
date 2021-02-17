#import librosa
#import librosa.display
#!/usr/bin/python 
# based on : www.daniweb.com/code/snippet263775.html
import math
import wave
import struct
import urllib.request
from html.parser import HTMLParser

# Audio will contain a long list of samples (i.e. floating point numbers describing the
# waveform).  If you were working with a very long sound you'd want to stream this to
# disk instead of buffering it all in memory list this.  But most sounds will fit in 
# memory.
audio = []
sample_rate = 16000.0
#坊ちゃん
#def_url = "https://www.aozora.gr.jp/cards/000148/files/752_14964.html"
#Qiita記事
#def_url = "https://qiita.com/hoto17296/items/8fcf55cc6cd823a18217"
#The Wonderful Wizard of Oz
def_url = "http://www.gutenberg.org/files/55/55.txt"

#simple html
#def_url = "https://elix.jp/ir/"

def append_sinPulse(_audio, _sample_rate=16000, _pulse_hz=1200, _pulseNum=1, _volume=0.75):
    per_samples = sample_rate / _pulse_hz
    for x in range(int(_pulseNum * per_samples)):
        val =  _volume * math.sin(2 * math.pi * ( x / per_samples ));
        _audio.append(val)

def bytes_to_tone(_data:bytes, _audio, _sample_rate=16000, _pulse_hz=1200, _volume=0.75, _max_bytes=100000):
    if(_max_bytes<=0):
        _max_bytes = len(_data)
    else:
        _max_bytes = min(_max_bytes,len(_data))
        
    for idx in range(_max_bytes):
        bstr="0"
        append_sinPulse(_audio, _sample_rate, _pulse_hz, 1, 0.75) # start bit 
        for b in range(8):
            onbit = ((_data[idx]>>b)&1)+1 # off=1,on=2
            bstr += str(onbit-1)
            append_sinPulse(_audio, _sample_rate, _pulse_hz*onbit, 1, 0.75) # data bit 

        append_sinPulse(_audio, _sample_rate, _pulse_hz*2, 2, 0.75) # stop bit 
        bstr += "11"
        print(bstr)
        

def append_silence(duration_milliseconds=500):
    """
    Adding silence is easy - we add zeros to the end of our array
    """
    num_samples = duration_milliseconds * (sample_rate / 1000.0)

    for x in range(int(num_samples)): 
        audio.append(0.0)

    return


def save_wav(file_name):
    print("saving ",file_name)
    # Open up a wav file
    wav_file=wave.open(file_name,"w")

    # wav params
    nchannels = 1

    sampwidth = 2

    # 44100 is the industry standard sample rate - CD quality.  If you need to
    # save on file size you can adjust it downwards. The stanard for low quality
    # is 8000 or 8kHz.
    nframes = len(audio)
    comptype = "NONE"
    compname = "not compressed"
    wav_file.setparams((nchannels, sampwidth, sample_rate, nframes, comptype, compname))

    # WAV files here are using short, 16 bit, signed integers for the 
    # sample size.  So we multiply the floating point data we have by 32767, the
    # maximum value for a short integer.  NOTE: It is theortically possible to
    # use the floating point -1.0 to 1.0 data directly in a WAV file but not
    # obvious how to do that using the wave module in python.
    for sample in audio:
        wav_file.writeframes(struct.pack('h', int( sample * 32767.0 )))

    wav_file.close()

    return


req = urllib.request.Request(def_url)
with urllib.request.urlopen(req) as res:
    body = res.read()
print(res.status)


class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.planeText = ""

    def handle_data(self, data):
        self.planeText += data
        print("Encountered some data  :", data)

utf8str="?"
try:
    utf8str=body.decode('utf-8')
except UnicodeDecodeError:
    pass

print("--------------------------------------------------------------------")
print("utf8str=",utf8str)
print("--------------------------------------------------------------------")
parser = MyHTMLParser()
parser.feed(utf8str)

bindata = parser.planeText.encode()

print (parser.planeText)
print("--------------------------------------------------------------------")
print (bindata)
print("--------------------------------------------------------------------")

datCnt=0
for data in bindata:
    print(data,)
    datCnt+=1
    if(datCnt>20):
        break


#http://ngs.no.coocan.jp/doc/wiki.cgi/TechHan?page=2%BE%CF+%A5%AB%A5%BB%A5%C3%A5%C8%8E%A5%A5%A4%A5%F3%A5%BF%A1%BC%A5%D5%A5%A7%A5%A4%A5%B9
append_sinPulse(audio, 16000,2400,16000,0.5) # long header
bytes_to_tone(b'\xd3\xd3\xd3\xd3\xd3\xd3\xd3\xd3\xd3\xd3', audio, 16000, 1200,0.75,1000) #0xD3 x 10
bytes_to_tone(b'myprog.cas', audio, 16000, 1200,0.75,1000) # filename
append_silence(1700) # space
append_sinPulse(audio, 16000,2400,4000,0.5) # short header
bytes_to_tone(bindata, audio, 16000, 1200,0.75,10000) # data body
append_sinPulse(audio, 16000,1200,7,0.5) # end of data

save_wav("output2.wav")
