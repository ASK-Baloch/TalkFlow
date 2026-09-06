
def parse_logs(filepath):
    events = []
    
    with open(filepath, 'r') as f:
        for line in f:
            if "probability=" in line: continue
            if "VAD" in line or "ASR" in line or "TTS" in line or "Qualification" in line or "AudioSocket" in line:
                # Assuming lines start with some standard format, we can just print them first to see
                events.append(line.strip())
                
    with open('timeline.txt', 'w') as f:
        f.writelines(e + "\n" for e in events)
            
if __name__ == "__main__":
    parse_logs("ai-gateway_live.log")
