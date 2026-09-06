# Benchmarks

## Phase 5: Pre-generated TTS

| Metric | Result |
| :--- | :--- |
| Asset count | 45 |
| Voice | af_heart/current |
| Source model | Kokoro v1.0 |
| Target PCM | 8k PCM16 mono |
| Redis hit P50 | ~80 ms |
| Redis hit P95 | ~85 ms |
| First audio Average | 416.2 ms |
| First audio P95 | 1155.0 ms |
| End-of-speech → first audio P50 | ~1100 ms |
| End-of-speech → first audio P95 | ~1200 ms |
| Playback errors | 0 |
| Queue overflows | 0 |

*(Note: Time metrics derived from small-scale integration test samples. True statistical P50/P95 pending larger scale load testing to adhere to no-fabrication policy).*

## Chatterbox Generative TTS (Phase 6)

Tested in an isolated local worker over an HTTP network hop from the AI Gateway. Since the backend does not support native streaming, the Time To First Audio (TTFA) equals the total synthesis time. 

| Words | Chars | TTFB (s) | Total (s) | Audio (s) | RTF   | Peak VRAM | Peak CPU |
| :---  | :---  | :---     | :---      | :---      | :---  | :---      | :---     |
| 1     | 4     | 6.417    | 6.417     | 1.360     | 4.719 | 3906 MB   | 77.9%    |
| 4     | 19    | 6.674    | 6.675     | 2.080     | 3.209 | 3906 MB   | 94.6%    |
| 9     | 46    | 10.342   | 10.345    | 3.240     | 3.193 | 3906 MB   | 90.9%    |
| 26    | 131   | 20.354   | 20.357    | 7.240     | 2.812 | 3906 MB   | 100.0%   |

### Key Takeaways
1. **Target conversational brevity:** Outputting short bursts (3-8 words) restricts the static blocking generation latency to ~6 seconds. Full paragraphs (25+ words) will push TTFA above 20 seconds.
2. **Resource demands:** The TTS neural generation runs hot, fully saturating the CPU up to 100%, emphasizing the necessity of isolating the TTS worker in a standalone process.
