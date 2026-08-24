# TalkFlow Medicare AI Voice Bot

Real-time, low-latency AI voice agent for Medicare qualification.

## Architecture

Asterisk/VICIdial
        |
        v
Real-Time AI Gateway
        |
        +-- VAD
        +-- Streaming ASR
        +-- Qualification Engine
        +-- Local LLM
        +-- Response Planner
        +-- Streaming TTS
        |
        +-- Redis
        +-- PostgreSQL
        +-- Kafka

Next.js Dashboard
        |
        +-- Campaigns
        +-- Scripts
        +-- Calls
        +-- Recordings
        +-- Analytics