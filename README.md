# SteganAudio

This is a Python3 Program to hide messages in Audio Files (currently only WAV Files are supported but I am working on other formats too). The tool is based on [HiddenWave](https://github.com/techchipnet/HiddenWave) by [TechChip](https://github.com/techchipnet).

The name "SteganAudio" is the concatenation of Steganography and Audio. Steganography is the process of Hiding one type of data/file in other type of data/file. More information can be [found here](https://en.wikipedia.org/wiki/Steganography).

![Preview](./Images/steganaudio-preview.png)

The oversimplified working of the program is that it opens the Audio file as an Audio Object and then decodes the binary data. It then converts our message to binary form and then it concatenates the message data over the audio data and then renders/encodes the audio back again. This gives us an audio file with the message hidden in it.

Note: Here, I say the message is been hidden in the audio but it isn't literally "hidden". In fact, using a spectrum analyzer, you can clearly see the difference between the original audio and the processed audio (which I will be showing later in this document). Using a fairly good speaker or pair of headphones, you can actually hear a faint noise along with a constant tone.

