#gs://catalobyte-output/1sPcgixNZobTGi1McrKK7UyaZUd2/o6h0z2g9c7/6681771295/1639832883748.flac

#from google.cloud import speech_v1
from google.cloud import speech
from google.cloud.speech_v1 import enums
from google.cloud.speech_v1 import types
import subprocess
#from pydub.utils import mediainfo
import subprocess
import math
import datetime
import srt


def long_running_recognize(storage_uri):
    
    client = speech.SpeechClient()

    config = {
        "language_code": "pt-BR",
        "sample_rate_hertz": 16000,
        #"encoding": enums.RecognitionConfig.AudioEncoding.LINEAR16,
        "encoding": "FLAC",
        "audio_channel_count": 1,
        "max_alternatives": 1,
        "enable_word_time_offsets": True,
        #"model": "video",
        "enable_automatic_punctuation":True
    }
    audio = {"uri": storage_uri}

    operation = client.long_running_recognize(config, audio)

    print(u"Waiting for operation to complete...")
    response = operation.result()
    
    return response

def subtitle_generation(response):
    bin_size=3.5
    """We define a bin of time period to display the words in sync with audio. 
    Here, bin_size = 3 means each bin is of 3 secs. 
    All the words in the interval of 3 secs in result will be grouped togather."""
    transcriptions = []
    index = 0
 
    for result in response.results:
        try:
            if result.alternatives[0].words[0].start_time.seconds:
                # bin start -> for first word of result
                start_sec = result.alternatives[0].words[0].start_time.seconds 
                start_microsec = result.alternatives[0].words[0].start_time.nanos * 0.001
            else:
                # bin start -> For First word of response
                start_sec = 0
                start_microsec = 0 
            end_sec = start_sec + bin_size # bin end sec
            
            # for last word of result
            last_word_end_sec = result.alternatives[0].words[-1].end_time.seconds
            last_word_end_microsec = result.alternatives[0].words[-1].end_time.nanos * 0.001
            
            # bin transcript
            transcript = result.alternatives[0].words[0].word
            
            index += 1 # subtitle index

            for i in range(len(result.alternatives[0].words) - 1):
                try:
                    word = result.alternatives[0].words[i + 1].word
                    word_start_sec = result.alternatives[0].words[i + 1].start_time.seconds
                    word_start_microsec = result.alternatives[0].words[i + 1].start_time.nanos * 0.001 # 0.001 to convert nana -> micro
                    word_end_sec = result.alternatives[0].words[i + 1].end_time.seconds
                    word_end_microsec = result.alternatives[0].words[i + 1].end_time.nanos * 0.001

                    if word_end_sec < end_sec:
                        transcript = transcript + " " + word
                    else:
                        previous_word_end_sec = result.alternatives[0].words[i].end_time.seconds
                        previous_word_end_microsec = result.alternatives[0].words[i].end_time.nanos * 0.001
                        
                        # append bin transcript
                        transcriptions.append(srt.Subtitle(index, datetime.timedelta(0, start_sec, start_microsec), datetime.timedelta(0, previous_word_end_sec, previous_word_end_microsec), transcript))
                        
                        # reset bin parameters
                        start_sec = word_start_sec
                        start_microsec = word_start_microsec
                        end_sec = start_sec + bin_size
                        transcript = result.alternatives[0].words[i + 1].word
                        
                        index += 1
                except IndexError:
                    pass
            # append transcript of last transcript in bin
            transcriptions.append(srt.Subtitle(index, datetime.timedelta(0, start_sec, start_microsec), datetime.timedelta(0, last_word_end_sec, last_word_end_microsec), transcript))
            index += 1
        except IndexError:
            pass
    
    # turn transcription list into subtitles
    subtitles = srt.compose(transcriptions)

    return subtitles


gcs_uri = f"gs://catalobyte-output/1sPcgixNZobTGi1McrKK7UyaZUd2/o6h0z2g9c7/5205870402/1639862253692.flac"
response=long_running_recognize(gcs_uri)
subtitle_generation(response)



subtitles= subtitle_generation(response)
srt_file = "video-subtitles.srt"
f = open(srt_file, 'w')
f.writelines(subtitles)
f.close()
