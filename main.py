import Audio
from AI import Nova, TranscribeSpeech, Functions

def MainLoop():
    AudioDevice = Audio.AudioDevice()
    NovaManager = Nova()

    while True:
        AudioDevice.Record()
        UserText = TranscribeSpeech("UserAudio.wav")

        NovaManager.add_message_to_thread(
            role="user",
            content=UserText
            )  
        NovaManager.run_assistant()
        Response = NovaManager.wait_for_completed()

        AudioDevice.Speak(Response)  
def test():  
    FunctionsManager = Functions()
    print(FunctionsManager.get_DateTime()[17::])
    for event in FunctionsManager.get_events({"date":FunctionsManager.get_DateTime()[17::]}).get("items",[]):
        print(event["summary"],event["start"])

  
if __name__ == "__main__":
    MainLoop()
    #test()  
