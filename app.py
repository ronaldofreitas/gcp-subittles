# -*- coding: utf-8 -*-




import srt
from google.cloud import speech

def long_running_recognize(storage_uri, idioma):
    client = speech.SpeechClient()

    # Encoding of audio data sent.
    operation = client.long_running_recognize(
        config=
        {
            "enable_word_time_offsets": True,
            "enable_automatic_punctuation": True,
            "sample_rate_hertz": 16000,
            "language_code": idioma,
            "audio_channel_count": 1,
            "encoding": "FLAC",
            "max_alternatives":1
        },
        audio={"uri": storage_uri},
    )
    response = operation.result()

    subs = []
    #pala = ''
    for result in response.results:
        # First alternative is the most probable result
        
        #pala += result.alternatives[0].transcript
        #print(result.alternatives[0].transcript)
        subs = break_sentences(40, subs, result.alternatives[0])

    #print(pala)
    return subs


def break_sentences(max_chars, subs, alternative):
    firstword = True
    charcount = 0
    idx = len(subs) + 1
    content = ""

    for w in alternative.words:
        if firstword:
            # first word in sentence, record start time
            start = w.start_time.ToTimedelta()

        charcount += len(w.word)
        content += " " + w.word.strip()
        
        if ("." in w.word or "!" in w.word or "?" in w.word or charcount > max_chars or
                ("," in w.word and not firstword)):
            # break sentence at: . ! ? or line length exceeded
            # also break if , and not first word
            subs.append(srt.Subtitle(index=idx,
                                     start=start,
                                     end=w.end_time.ToTimedelta(),
                                     content=srt.make_legal_content(content)))
            firstword = True
            idx += 1
            content = ""
            charcount = 0
        else:
            firstword = False
    return subs


def write_srt(subs):
    srt_file = "legenda.srt"
    f = open(srt_file, 'w')
    f.writelines(srt.compose(subs))
    f.close()
    return


def write_txt(subs):
    txt_file = "texto.txt"
    f = open(txt_file, 'w')
    for s in subs:
        f.write(s.content.strip() + "\n")
    f.close()
    return


storage_uri = "gs://catalobyte-output/1sPcgixNZobTGi1McrKK7UyaZUd2/o6h0z2g9c7/6826041503/1639855787393.flac"
idioma = "pt-BR"
subs = long_running_recognize(storage_uri, idioma)
write_srt(subs)
write_txt(subs)
