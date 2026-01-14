from g2p_en import G2p

g2p = G2p()

def text_to_phonemes(sentence):
    """
    Convert sentence text to phoneme sequence
    """
    phonemes = g2p(sentence)
    phonemes = [p for p in phonemes if p.isalpha()]
    return phonemes
